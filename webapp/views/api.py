import base64
from json import dumps

import requests
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from flask import request, make_response, Response
from Crypto.Hash import SHA512, SHA256
from core.module import Module
from services.Cipher import AESCipher, merchant_decrypt_k1, decrypt_aes, ds_check, encrypt_rsa, sign_message, \
    decrypt_rsa, verify_rsa, encrypt_aes
from services.converter import bytes_to_array, hex_to_bytes, hex_to_array, json
import json as JSON

from services.keys import paymentgateway, merchant

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/make_purchase_request')
def make_purchase_request():
    data = request.form.to_dict()
    print(data)

    pomd = data.get('pomd')
    pimd = data.get('pimd')
    oimd = data.get('oimd')

    print("POMD", pomd)
    print("PIMD", pimd, hex_to_array(pimd))
    print("OIMD", oimd, hex_to_array(oimd))

    # Decrypt k1 and k2
    k1_encrypted = data['k1_encrypted']
    k1 = merchant_decrypt_k1(k1_encrypted)

    #
    merchant_part = data.get('merchant_part')
    merchant_part = JSON.loads(merchant_part)
    print("merchant_part", merchant_part)

    # Decrypt DS
    iv1 = data['iv1']
    ds = merchant_part['ds']
    pomd_from_ds = decrypt_aes(k1, iv1, ds)
    oi = merchant_part['oi']

    response =  None
    ds_check(pimd, oi, ds, k1, iv1, True)
    if ds_check(pimd, oi, ds, k1, iv1, True):
        authdata = 'hi here is the payment information'

        #Encrypt Authdata
        k3 = Random.get_random_bytes(16)
        aes = AESCipher(k3)
        authdata_encrypted = aes.encrypt(authdata)

        #Encrypt K3
        kupg = paymentgateway.publickey()
        k3_encrypted = encrypt_rsa(kupg, k3)

        #Sign hash_authdata
        krm = merchant
        authdata_signature = sign_message(krm, authdata.encode())
        print("authdata_signature", authdata_signature)

        #encrypt k1 with kupg
        kupg = paymentgateway.publickey()
        k1_encrypted = encrypt_rsa(kupg, k1)

        #Base64 Encode
        b64_authdata_encrypted = base64.b64encode(authdata_encrypted)
        b64_k3_encrypted = base64.b64encode(k3_encrypted)
        b64_authdata_signature = base64.b64encode(authdata_signature)
        b64_k1_encrypted = base64.b64encode(k1_encrypted)


        gateway_part_encrypted = data.get('gateway_part_encrypted')
        k2_encrypted = data.get('k2_encrypted')
        iv2 = data.get('iv2')

        gateway_response = requests.post("http://0.0.0.0:8002/test",
                                      data={'b64_authdata_encrypted': b64_authdata_encrypted,
                                            'b64_k3_encrypted': b64_k3_encrypted,
                                            'b64_authdata_signature': b64_authdata_signature,
                                            'gateway_part_encrypted': gateway_part_encrypted,
                                            'k2_encrypted': k2_encrypted,
                                            'iv2': iv2,
                                            'iv1': iv1,
                                            'b64_k1_encrypted':b64_k1_encrypted})

        if gateway_response.status_code == 200:
            print("gateway_response", gateway_response.content)
            gateway_response = gateway_response.json()['data']

            if 'b64_bankcertificate' not in gateway_response:
                msg = 'Response Without Bank Certificate'
                response = make_response(json({'status': 'NO', 'message': msg}))

            #Fetch Data
            b64_authresponse_encrypted = gateway_response.get('b64_authresponse_encrypted').encode()
            b64_k4_encrypted = gateway_response.get('b64_k4_encrypted').encode()
            b64_authresponse_signature = gateway_response.get('b64_authresponse_signature').encode()
            b64_bankcertificate = gateway_response.get('b64_bankcertificate').encode()

            #Decode b64
            authresponse_encrypted = base64.b64decode(b64_authresponse_encrypted)
            k4_encrypted = base64.b64decode(b64_k4_encrypted)
            authresponse_signature = base64.b64decode(b64_authresponse_signature)
            bankcertificate = base64.b64decode(b64_bankcertificate)

            #Decrypt K4
            k4 = decrypt_rsa(krm, k4_encrypted)

            #Decrypt authresponse
            authresponse = AESCipher(k4).decrypt(authresponse_encrypted)

            #Verify Signature
            if not verify_rsa(kupg, authresponse, authresponse_signature):
                msg = "couldnt verify gateway response"
                response = make_response(json({'status': 'NO', 'message': msg}))

            print("authresponse", authresponse)
            if authresponse == b'cool, here is my certificate':
                authdata = 'everything is good'

                #Encrypt authdata
                k5 = Random.get_random_bytes(16)
                authdata_encrypted = encrypt_aes(k5, authdata)

                #Encrypt K5 with Krm and K1
                print("k5", k5, bytes_to_array(k5))
                k5_b64 = base64.b64encode(k5)
                print("k5_b64", k5_b64)
                k5_b64_encrypted = encrypt_aes(k1, k5_b64.decode())
                print("k5_b64_encrypted", k5_b64_encrypted)

                #sign authdata_hash
                authdata_signature = sign_message(krm, authdata.encode())

                #Base64 Encode
                b64_authdata_encrypted = base64.b64encode(authdata_encrypted)
                b64_k5_b64_encrypted = base64.b64encode(k5_b64_encrypted)
                b64_authdata_signature = base64.b64encode(authdata_signature)

                response = make_response(json({'status': 'OK',
                                               'action': 'password',
                                               'b64_authdata_encrypted': b64_authdata_encrypted.decode(),
                                               'b64_k5_b64_encrypted': b64_k5_b64_encrypted.decode(),
                                               'b64_authdata_signature': b64_authdata_signature.decode(),
                                               'url': 'https://0.0.0.0:8000/shop/password'}))
            else:
                response = make_response(json({'status': 'NO', 'message': authresponse.decode()}))
            return response

        msg = "can't communicate with gateway"
        response = make_response(json({'status': 'NO', 'message': msg}))
    else:
        msg = 'message went wrong during transmission, hashes dont match'
        response = make_response(json({'status': 'NO', 'message': msg}))

    return response


