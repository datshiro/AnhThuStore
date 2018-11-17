from services.certificate_helper import CertificateHelper

def get_key(owner, use_type):
    cert_helper = CertificateHelper(owner, use_type)
    cert = cert_helper.get_cert_key()
    return cert