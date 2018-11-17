import datetime

import requests
from flask import make_response

from common.messages import ErrorMessages
from models.certificate_key import CertificateKey, DoesNotExist
from services.converter import json as custom_json

from common.constants import Api


class CertificateHelper(object):
    owner = None
    use_type = None

    def __init__(self, owner, use_type):
        self.owner = owner
        self.use_type = use_type

    @classmethod
    def request_certificate(self):
        response = requests.post(Api.REQUEST_CERTIFICATE)

        if response.status_code != 200:
            make_response(
                custom_json({'status': 'NO', 'message': ErrorMessages.FAILED_RENEW_CERTIFICATE.format(self.name)}))

        data = response.json()['data']
        public_key = data.get('public_key')
        private_key = data.get('private_key')
        return public_key, private_key

    def get_cert_key(self):
        if not self.owner and not self.use_type:
            raise ValueError('Invalid value to generate certificate: name=' + self.owner + '; use_type=' + self.use_type)
        try:
            cert = CertificateKey.objects.get(key_owner=self.owner, use_type=self.use_type)
            if datetime.utcnow() - cert.created_at > 1:
                # Expired Key
                cert = self.request_certificate()
        except DoesNotExist:
            cert = self.request_certificate()
        return cert

