import base64
import json

from flask import request, make_response

from common.constants import BankCertificates
from common.messages import Messages, ErrorMessages
from core.module import Module
from models.bank_session import BankSession
from models.card import Card, DoesNotExist
from services.Cipher import decrypt_rsa
from services.converter import json as custom_json
from services.keys import bank

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/authorization')
def authorization():
    data = request.form.to_dict()

    session_id = data.get('session_id')
    kuis = bank.publickey().exportKey()
    b64_kuis = base64.b64encode(kuis)

    authdata = data.get('authdata')
    if authdata == Messages.AUTH_REQUEST:
        pi = data.get('pi')
        pi = json.loads(pi)
        try:
            card_id = pi.get('card_id')
            card = Card.objects.get(pk=card_id)
            if card:
                bank_session = BankSession(id=session_id)
                bank_session.data = pi
                bank_session.save()

                return make_response(custom_json(
                    {'authresponse': Messages.AUTH_RESPONSE, 'bankcertificate': BankCertificates.VCB,
                     'b64_kuis': b64_kuis.decode()}))
        except DoesNotExist:
            return make_response(custom_json(
                {'authresponse': ErrorMessages.INVALID_CARD, 'bankcertificate': BankCertificates.VCB, 'b64_kuis': b64_kuis.decode()}))

    return make_response(custom_json(
        {'authresponse': ErrorMessages.INVALID_AUTH_REQUEST, 'bankcertificate': BankCertificates.VCB, 'b64_kuis': b64_kuis.decode()}))


@module.get_post('/password')
def password():
    data = request.form.to_dict()
    session_id = data.get('session_id')

    # Fetch Data
    b64_authdata = data.get('b64_authdata')
    b64_pwd_kuisencrypted = data.get('b64_pwd_kuisencrypted')

    # Decode base64
    authdata = base64.b64decode(b64_authdata)
    pwd_kuisencrypted = base64.b64decode(b64_pwd_kuisencrypted)

    # Decrypt pwd_kuisencrypted
    kris = bank
    pwd = decrypt_rsa(kris, pwd_kuisencrypted)

    bank_session = BankSession.objects.get(pk=session_id)
    card_id = bank_session.data.get('card_id')

    try:
        card = Card.objects.get(pk=card_id, password=pwd.decode())
    except DoesNotExist:
        return make_response(custom_json({'payment_response': 'the otp does not matches'}))

    return make_response(custom_json({'payment_response': Messages.TRANSACTION_VERIFIED}))
