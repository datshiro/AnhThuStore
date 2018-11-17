class BankCertificates(object):
    VCB = "VCB-DATSHIRO"
    VPB = "VPB-EMILIOANH"


class Ports(object):
    MERCHANT = 8000
    VCB_BANK = 8003
    GATEWAY = 8002
    CA = 8005
    ACQUIRER = 8006


class Api(object):
    BANK_AUTHORIZE = "http://0.0.0.0:{}/api/authorization".format(Ports.VCB_BANK)
    SEND_BANK_PASSWORD = "http://0.0.0.0:{}/api/password"   # use format() with relevant bank
    SEND_GATEWAY_PASSWORD = "http://0.0.0.0:{}/password".format(Ports.GATEWAY)
    REQUEST_CERTIFICATE = "http://0.0.0.0:{}/gen_certificate".format(Ports.CA)

