import base64
from json import dumps

import requests
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from flask import request, make_response, Response
from Crypto.Hash import SHA512, SHA256
from core.module import Module
from services.Cipher import AESCipher, merchant_decrypt_k1, decrypt_aes, ds_check, encrypt_rsa, sign_message
from services.converter import bytes_to_array, hex_to_bytes, hex_to_array
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

        response_test = requests.post("http://0.0.0.0:8002/test",
                                      data={'b64_authdata_encrypted': b64_authdata_encrypted,
                                            'b64_k3_encrypted': b64_k3_encrypted,
                                            'b64_authdata_signature': b64_authdata_signature,
                                            'gateway_part_encrypted': gateway_part_encrypted,
                                            'k2_encrypted': k2_encrypted,
                                            'iv2': iv2,
                                            'iv1': iv1,
                                            'b64_k1_encrypted':b64_k1_encrypted})
        print(response_test)

        response = make_response(json({'status': 'OK'}))
    else:
        response = make_response(json({'status': 'NO'}))

    # Decrypt Merchant part
    # merchant_part_encrypted = bytes_to_array(merchant_part_encrypted.encode())
    # print("IV1", iv1)
    # print("merchant_part_encrypted", merchant_part_encrypted )
    # aes = AESCipher(k1)
    # merchant_part = aes.decrypt(bytes(iv1+merchant_part_encrypted))
    # print(merchant_part)

    return response


def json(data):
    """
    This is the function, which return json data
    """
    return Response(dumps({'data': data}), mimetype='application/json')
