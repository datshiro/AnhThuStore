import requests
from flask import make_response

from common.messages import ErrorMessages
from services.converter import json as custom_json

from common.constants import Api


class CertificateHelper(object):
    name = None

    def __init__(self, name):
        self.name = name

    def request_certificate(self):
        response = requests.post(Api.REQUEST_CERTIFICATE)

        if response.status_code != 200:
            make_response(
                custom_json({'status': 'NO', 'message': ErrorMessages.FAILED_RENEW_CERTIFICATE.format(self.name)}))

        data = response.json()['data']
        public_key = data.get('public_key')
        private_key = data.get('private_key')
        return public_key, private_key
