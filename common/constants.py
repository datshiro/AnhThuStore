class BankCertificates(object):
    VCB = "VCB-DATSHIRO"


class Api(object):
    BANK_AUTHORIZE = "http://0.0.0.0:8003/api/authorization"
    SEND_BANK_PASSWORD = "http://0.0.0.0:8003/api/password"
    SEND_GATEWAY_PASSWORD = "http://0.0.0.0:8002/password"
