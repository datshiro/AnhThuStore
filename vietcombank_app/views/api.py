import base64
import json

from flask import request, make_response, Response

from core.module import Module
from models.card import Card, DoesNotExist
from services.Cipher import decrypt_rsa
from services.converter import json as custom_json
from services.keys import bank

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/authorization')
def authorization():
    data = request.form.to_dict()
    print(data)

    authdata = data.get('authdata')
    if authdata == 'hi here is the payment information':
        pi = data.get('pi')
        pi = json.loads(pi)
        auth_response = ""
        try:
            card_id = pi.get('card_id')
            card = Card.objects.get(pk=card_id)
            if card:
                print('cool, here is my certificate')
                kuis = bank.publickey().exportKey();
                b64_kuis = base64.b64encode(kuis)
                print("request", request)
                return make_response(custom_json({'authresponse': 'cool, here is my certificate', 'bankcertificate': 'VCB-DATSHIRO', 'b64_kuis': b64_kuis.decode()}))
                # return make_response(Response(json.dumps({'authresponse': 'cool, here is my certificate', 'bankcertificate': 'VCB-DATSHIRO'}), mimetype='application/json'))
        except DoesNotExist:
            auth_response = "Invalid Card ID"
            return make_response(custom_json({'authresponse': auth_response, 'bankcertificate': 'VCB-DATSHIRO'}))
            # return make_response(Response(
            #     json.dumps({'authresponse': auth_response, 'bankcertificate': 'VCB-DATSHIRO'}),
            #     mimetype='application/json'))

    # return make_response(Response(json.dumps({'authresponse': 'unknown authrequest'}), mimetype='application/json'))
    return make_response(custom_json({'authresponse': 'unknown authrequest'}))


@module.get_post('/password')
def password():
    data = request.form.to_dict()

    #Fetch Data
    b64_authdata = data.get('b64_authdata')
    b64_pwd_kuisencrypted = data.get('b64_pwd_kuisencrypted')

    #Decode base64
    authdata = base64.b64decode(b64_authdata)
    pwd_kuisencrypted = base64.b64decode(b64_pwd_kuisencrypted)

    #Decrypt pwd_kuisencrypted
    kris = bank
    pwd = decrypt_rsa(kris,pwd_kuisencrypted)

    print("password", pwd)
    return make_response(custom_json({'payment_response': 'the otp matches'}))
