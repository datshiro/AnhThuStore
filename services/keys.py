from Crypto.PublicKey import RSA

from services.certificate_helper import CertificateHelper
from common.constants import CertificateOwner, CertificateType

bank_key = open('bank.pem')

merchant_key = open('merchant.pem')


# paymentgateway_key = open('payment.pem')
def get_key(owner, use_type):
    cert_helper = CertificateHelper(owner, use_type)
    cert = cert_helper.get_cert_key()
    return cert


bank = RSA.importKey(bank_key.read())

merchant = RSA.importKey(merchant_key.read())

# paymentgateway = RSA.importKey(paymentgateway_key.read())
# paymentgateway = get_key(CertificateOwner.GATEWAY, CertificateType.GATEWAY)
