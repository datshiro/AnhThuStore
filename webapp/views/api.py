import base64
from json import dumps

import requests
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from flask import request, make_response, Response, render_template
from Crypto.Hash import SHA512, SHA256
from flask_mail import Message

from core.module import Module
from models.cart import Cart
from models.product import Product
from services.Cipher import AESCipher, merchant_decrypt_k1, decrypt_aes, ds_check, encrypt_rsa, sign_message, \
    decrypt_rsa, verify_rsa, encrypt_aes
from services.converter import bytes_to_array, hex_to_bytes, hex_to_array, json
import json as JSON

from services.keys import paymentgateway, merchant
from settings import SESSION_KEY

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/make_purchase_request')
def make_purchase_request():
    data = request.form.to_dict()
    print(data)
    session_id = request.cookies.get(SESSION_KEY)
    print("session_id", session_id)
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
                                            'b64_k1_encrypted':b64_k1_encrypted,
                                            'session_id': request.cookies.get(SESSION_KEY)})

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
            b64_kuis = gateway_response.get('b64_kuis').encode()

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
                b64_bankcertificate = base64.b64encode(bankcertificate)

                response = make_response(json({'status': 'OK',
                                               'action': 'password',
                                               'b64_authdata_encrypted': b64_authdata_encrypted.decode(),
                                               'b64_k5_b64_encrypted': b64_k5_b64_encrypted.decode(),
                                               'b64_authdata_signature': b64_authdata_signature.decode(),
                                               'b64_bankcertificate': b64_bankcertificate.decode(),
                                               'b64_kuis': b64_kuis.decode(),
                                               'url': 'https://0.0.0.0:8000/shop/password'}))
                session = request.session
                # print("oi", JSON.loads(oi))
                session.data = JSON.loads(oi)
                session.save()
            else:
                response = make_response(json({'status': 'NO', 'message': authresponse.decode()}))
            return response

        msg = "can't communicate with gateway"
        print("msg", msg)
        response = make_response(json({'status': 'NO', 'message': msg}))
    else:
        msg = 'message went wrong during transmission, hashes dont match'
        print("msg", msg)
        response = make_response(json({'status': 'NO', 'message': msg}))

    return response


@module.get_post('/password')
def password():
    data = request.form.to_dict()
    #Fetch Data
    k6_encrypted_kum = data.get('k6_encrypted_kum')
    k6_encrypted_kupg = data.get('k6_encrypted_kupg')
    iv6 = data.get('iv6')
    authdata_and_hashed_k6encrypted = data.get('authdata_and_hashed_k6encrypted')
    pwd_kuisencrypted_and_hashed_k6encrypted = data.get('pwd_kuisencrypted_and_hashed_k6encrypted')

    #Decrypt K6
    krm = merchant
    k6 = merchant_decrypt_k1(k6_encrypted_kum)

    print("authdata_and_hashed_k6encrypted", authdata_and_hashed_k6encrypted)
    #Decrypt Authdata
    authdata_and_hashed = decrypt_aes(k6, iv6, authdata_and_hashed_k6encrypted)
    authdata = authdata_and_hashed[:-32]
    hashed = authdata_and_hashed[len(authdata):]

    print("authdata_and_hashed", authdata_and_hashed, type(authdata_and_hashed))

    #Hash authdata
    authdata_hashed = SHA256.new(authdata).hexdigest()
    authdata_hashed = bytes.fromhex(authdata_hashed)
    print("authdata_hashed", authdata_hashed)
    print("hashed", hashed)

    if not authdata_hashed == hashed:
        msg = "message went wrong during transmission, hashes dont match"
        return make_response(json({'status': 'NO', 'message': msg}))

    #Encrypt AuthData with k7
    k7 = Random.get_random_bytes(16)
    authdata_encrypted_k7 = encrypt_aes(k7, authdata.decode())

    #Encrypt K7 with Kupg
    kupg = paymentgateway.publickey()
    k7_encrypted_kupg = encrypt_rsa(kupg, k7)

    print("k7_encrypted_kupg", k7_encrypted_kupg)
    print("k6_encrypted_kupg", k6_encrypted_kupg)
    #Sign authdata_encrypted_k7 with Krm
    authdata_signature = sign_message(krm,authdata)

    print("pwd_kuisencrypted_and_hashed_k6encrypted", pwd_kuisencrypted_and_hashed_k6encrypted)
    #Base64 Encode
    b64_pwd_kuisencrypted_and_hashed_k6encrypted = base64.b64encode(pwd_kuisencrypted_and_hashed_k6encrypted.encode())
    b64_k7_encrypted_kupg = base64.b64encode(k7_encrypted_kupg)
    b64_authdata_signature = base64.b64encode(authdata_signature)
    b64_authdata_encrypted_k7 = base64.b64encode(authdata_encrypted_k7)
    b64_k6_encrypted_kupg = base64.b64encode(k6_encrypted_kupg.encode())
    b64_iv6 = base64.b64encode(iv6.encode())

    gateway_response = requests.post("http://0.0.0.0:8002/password",
                                     data={'b64_pwd_kuisencrypted_and_hashed_k6encrypted': b64_pwd_kuisencrypted_and_hashed_k6encrypted.decode(),
                                           'b64_k7_encrypted_kupg': b64_k7_encrypted_kupg,
                                           'b64_authdata_signature': b64_authdata_signature,
                                           'b64_authdata_encrypted_k7': b64_authdata_encrypted_k7,
                                           'b64_k6_encrypted_kupg': b64_k6_encrypted_kupg,
                                           'b64_iv6': b64_iv6,
                                           'session_id': request.cookies.get(SESSION_KEY)})

    if gateway_response.status_code == 200:
        print("gateway_response", gateway_response.content)
        gateway_response = gateway_response.json()['data']

        if gateway_response.get('status') == 'YES':

            #Fetch Data
            b64_payment_response_encrypted = gateway_response.get('b64_payment_response_encrypted')
            b64_k8_encrypted_kum = gateway_response.get('b64_k8_encrypted_kum')
            b64_payment_response_signature = gateway_response.get('b64_payment_response_signature')

            #Decode base64
            payment_response_encrypted = base64.b64decode(b64_payment_response_encrypted)
            k8_encrypted_kum = base64.b64decode(b64_k8_encrypted_kum)
            payment_response_signature = base64.b64decode(b64_payment_response_signature)

            #Decrypt K8_KUM
            k8 = decrypt_rsa(krm, k8_encrypted_kum)

            #Decrypt payment_response_encrypted
            payment_response = AESCipher(k8).decrypt(payment_response_encrypted)

            if verify_rsa(kupg, payment_response, payment_response_signature):
                if (payment_response.decode() == 'the otp matches'):
                    cart = Cart.get_current()
                    products = cart.products
                    msg = render_template('mail_order.html', products=products, cart=cart)
                    user = request.session.user
                    from app import mail

                    message = Message(subject="Mua Hàng Thành Công",
                                      html=msg,
                                      sender=("Anh Thu Shop", "datshiro@gmail.com"),
                                      recipients=[user.email])
                    mail.send(message)
                    cart = Cart.get_current()
                    cart.data = {}
                    response = make_response(json({'status': 'YES', 'payment_response': payment_response.decode()}))
                    response.set_cookie('cart', cart.jsonified_data)
                    return response
                else:
                    msg = "the otp does not matches"
                    return make_response(json({'status': 'NO', 'message': msg}))

    msg="No response from gateway"
    return make_response(json({'status': 'NO', 'message': msg}))
    pass

@module.get('/test-mail')
def test_mail():
    cart = Cart.get_current()
    products = cart.products
    return render_template('mail_order.html', products=products, cart=cart)