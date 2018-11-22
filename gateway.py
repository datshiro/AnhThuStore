import base64

from flask import request, make_response
from flask import Flask
from flask import abort
from Crypto.Hash import SHA512, SHA256
import requests
import json as JSON

from flask_mongoengine import MongoEngine

import settings
from common.constants import Api, Ports, CertificateOwner, CertificateType, BankPorts
from common.messages import ErrorMessages
from services.cipher import AESCipher, decrypt_aes, decrypt_rsa, verify_rsa, ds_check, encrypt_aes, encrypt_rsa, sign_message
from services.converter import json
from services.keys import *
from Crypto import Random
from Crypto.PublicKey import RSA

app = Flask(__name__)
app.config.from_object(settings)
db = MongoEngine(app)

@app.route("/send-payment-info", methods=["POST", "GET"])
def send_payment_info():
    if not request.form:
        abort(400)

    data = request.form.to_dict()
    session_id = data.get('session_id')

    # Fetch data
    b64_authdata_encrypted = data.get('b64_authdata_encrypted', '')
    b64_k3_encrypted = data.get('b64_k3_encrypted')
    b64_authdata_signature = data.get('b64_authdata_signature')

    # Decode base64
    k3_encrypted = base64.b64decode(b64_k3_encrypted)
    authdata_encrypted = base64.b64decode(b64_authdata_encrypted)
    authdata_signature = base64.b64decode(b64_authdata_signature)

    # decrypt k3
    krpg = RSA.importKey(get_key(CertificateOwner.GATEWAY, CertificateType.GATEWAY)['private_key'])
    k3 = decrypt_rsa(krpg, k3_encrypted)

    # decrypt authdata
    aes = AESCipher(k3)
    authdata = aes.decrypt(authdata_encrypted)

    # verify hash_authdata_signature
    kum = RSA.importKey(get_key(CertificateOwner.MERCHANT, CertificateType.MERCHANT)['public_key'])

    if not verify_rsa(kum, authdata, authdata_signature):
        msg = ErrorMessages.FAILED_VERIFY_DATA
        return make_response(json(msg))

    # fetch data
    gateway_part_encrypted = data.get('gateway_part_encrypted')
    k2_encrypted = data.get('k2_encrypted')
    iv2 = data.get('iv2')
    iv1 = data.get('iv1')
    b64_k1_encrypted = data.get('b64_k1_encrypted')

    k1_encrypted = base64.b64decode(b64_k1_encrypted)

    # Decrypt k2_encrypted
    k2 = decrypt_rsa(krpg, bytes.fromhex(k2_encrypted))

    # Decrypt gateway_part_encrypted
    gateway_part = decrypt_aes(k2, iv2, gateway_part_encrypted)
    gateway_part = JSON.loads(gateway_part)

    # Fetch from gateway_part
    pi = gateway_part.get('pi')
    oimd = gateway_part.get('oimd')
    ds = gateway_part.get('ds')

    bank_name = JSON.loads(pi).get('bank_name', None)

    # Decrypt k1
    k1 = decrypt_rsa(krpg, k1_encrypted)

    if not ds_check(oimd, pi, ds, k1, iv1, merchant=False):
        msg = ErrorMessages.MISMATCH_DIGEST
        return make_response(json({'message': msg}))

    # TODO: check pi key "bank_name" to switch for address not http://0.0.0.0:8003/api/authorization
    response = requests.post(Api.BANK_AUTHORIZE.format(BankPorts[bank_name]),
                             data={'authdata': authdata, 'pi': pi, 'session_id': session_id})

    if response.status_code != 200:
        msg = ErrorMessages.FAILED_CONNECT_BANK
        return make_response(json({'message': msg}))

    bank_response = response.json()['data']

    authresponse = bank_response.get('authresponse')
    bankcertificate = bank_response.get('bankcertificate')
    b64_kuis = bank_response.get('b64_kuis')

    # Encrypt authresponse
    k4 = Random.get_random_bytes(16)
    authresponse_encrypted = encrypt_aes(k4, authresponse)

    # Encrypt K4
    k4_encrypted = encrypt_rsa(kum, k4)

    # Sign authresponse
    authresponse_signature = sign_message(krpg, authresponse.encode())

    # Encode Base64
    b64_authresponse_encrypted = base64.b64encode(authresponse_encrypted)
    b64_k4_encrypted = base64.b64encode(k4_encrypted)
    b64_authresponse_signature = base64.b64encode(authresponse_signature)
    b64_bankcertificate = base64.b64encode(bankcertificate.encode())

    return make_response(json({'b64_authresponse_signature': b64_authresponse_signature.decode(),
                               'b64_k4_encrypted': b64_k4_encrypted.decode(),
                               'b64_authresponse_encrypted': b64_authresponse_encrypted.decode(),
                               'b64_bankcertificate': b64_bankcertificate.decode(),
                               'b64_kuis': b64_kuis}))


@app.route("/password", methods=["POST"])
def password():
    data = request.form.to_dict()

    session_id = data.get('session_id')

    # Fetch data
    b64_pwd_kuisencrypted_and_hashed_k6encrypted = data.get('b64_pwd_kuisencrypted_and_hashed_k6encrypted')
    b64_k7_encrypted_kupg = data.get('b64_k7_encrypted_kupg')
    b64_authdata_signature = data.get('b64_authdata_signature')
    b64_authdata_encrypted_k7 = data.get('b64_authdata_encrypted_k7')
    b64_k6_encrypted_kupg = data.get('b64_k6_encrypted_kupg')
    b64_iv6 = data.get('b64_iv6')
    bank_name = data.get('bank_name', None)

    # Decode Base64
    pwd_kuis_encrypted_and_hashed_k6encrypted = base64.b64decode(b64_pwd_kuisencrypted_and_hashed_k6encrypted)
    k7_encrypted_kupg = base64.b64decode(b64_k7_encrypted_kupg)
    authdata_signature = base64.b64decode(b64_authdata_signature)
    authdata_encrypted_k7 = base64.b64decode(b64_authdata_encrypted_k7)
    k6_encrypted_kupg = base64.b64decode(b64_k6_encrypted_kupg)
    iv6 = base64.b64decode(b64_iv6)

    # Decrypt K7
    krpg = RSA.importKey(get_key(CertificateOwner.GATEWAY, CertificateType.GATEWAY)['private_key'])
    k7 = decrypt_rsa(krpg, k7_encrypted_kupg)

    # Decrypt AuthData
    authdata = AESCipher(k7).decrypt(authdata_encrypted_k7)

    # verify authdata_signature
    kum = RSA.importKey(get_key(CertificateOwner.MERCHANT, CertificateType.MERCHANT)['public_key'])
    if not verify_rsa(kum, authdata, authdata_signature):
        msg = ErrorMessages.MISMATCH_DIGEST
        return make_response(json({'message': msg}))

    # Decrypt K6 with Krpg
    from Crypto.Cipher import PKCS1_OAEP
    k6 = PKCS1_OAEP.new(krpg).decrypt(bytes.fromhex(k6_encrypted_kupg.decode()))

    # Decrypt pwd_kuis_encrypted_and_hashed_k6encrypted
    pwd_kuis_encrypted_and_hashed = decrypt_aes(k6, iv6.decode(), pwd_kuis_encrypted_and_hashed_k6encrypted.decode())
    pwd_kuis_encrypted = pwd_kuis_encrypted_and_hashed[:-32]
    hashed = pwd_kuis_encrypted_and_hashed[len(pwd_kuis_encrypted):]

    # Hash pwd_kuis_encrypted
    pwd_kuis_encrypted_hashed = SHA256.new(pwd_kuis_encrypted).hexdigest()
    pwd_kuis_encrypted_hashed = bytes.fromhex(pwd_kuis_encrypted_hashed)

    if not pwd_kuis_encrypted_hashed == hashed:
        msg = ErrorMessages.MISMATCH_DIGEST
        return make_response(json({'message': msg}))

    # Base64 Encode
    b64_authdata = base64.b64encode(authdata)
    b64_pwd_kuisencrypted = base64.b64encode(pwd_kuis_encrypted)

    bank_response = requests.post(Api.SEND_BANK_PASSWORD.format(Ports.VCB_BANK),
                                  data={'b64_authdata': b64_authdata,
                                        'b64_pwd_kuisencrypted': b64_pwd_kuisencrypted,
                                        'session_id': session_id,
                                        'bank_name': bank_name})
    if not bank_response.status_code == 200:
        msg = ErrorMessages.FAILED_CONNECT_BANK
        return make_response(json({'message': msg}))

    payment_response = bank_response.json()['data'].get('payment_response')

    # Encrypt payment_response
    k8 = Random.get_random_bytes(16)
    payment_response_encrypted = encrypt_aes(k8, payment_response)

    # Encrypt K8 with Kum
    k8_encrypted_kum = encrypt_rsa(kum, k8)

    # Sign payment_response
    payment_response_signature = sign_message(krpg, payment_response.encode())

    # Base64 Encode
    b64_payment_response_encrypted = base64.b64encode(payment_response_encrypted)
    b64_k8_encrypted_kum = base64.b64encode(k8_encrypted_kum)
    b64_payment_response_signature = base64.b64encode(payment_response_signature)

    return make_response(json({'status': 'YES',
                               'b64_payment_response_encrypted': b64_payment_response_encrypted.decode(),
                               'b64_k8_encrypted_kum': b64_k8_encrypted_kum.decode(),
                               'b64_payment_response_signature': b64_payment_response_signature.decode()}))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=Ports.GATEWAY)
