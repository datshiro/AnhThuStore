from mongoengine import *
from datetime import datetime


class CertificateKey(Document):
    key_owner = StringField(primary_key=True, max_length=255, verbose_name='Key Owner')
    created_at = DateTimeField(default=datetime.now)
    private_key = BinaryField(required=True, verbose_name='Private Key')
    public_key = BinaryField(required=True, verbose_name='Public Key')
    use_type = StringField(required=True, verbose_name='User Type')