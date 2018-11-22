class Banks(object):
    VCB = "Vietcombank"
    VPB = "VP Bank"


class BankCertificates(object):
    VCB = "VCB-DATSHIRO"
    VPB = "VPB-EMILIOANH"


class Ports(object):
    MERCHANT = 8000
    VCB_BANK = 8003
    VPB_BANK = 8007
    GATEWAY = 8002
    CA = 8005


class Api(object):
    BANK_AUTHORIZE = "http://0.0.0.0:{}/api/authorization"
    SEND_BANK_PASSWORD = "http://0.0.0.0:{}/api/password"  # use format() with relevant bank
    SEND_GATEWAY_PASSWORD = "http://0.0.0.0:{}/password".format(Ports.GATEWAY)
    REQUEST_CERTIFICATE = "http://0.0.0.0:{}/gen-certificate".format(Ports.CA)


class CertificateOwner(object):
    VCB_BANK = "VCB_BANK"
    VPB_BANK = "VP_BANK"
    GATEWAY = "GATEWAY"
    MERCHANT = "ANH_THU_STORE"


class CertificateType(object):
    BANK = "BANK"
    GATEWAY = "GATEWAY"
    MERCHANT = "MERCHANT"


BankUrls = {
    Banks.VCB: 'http://0.0.0.0:{}/'.format(Ports.VCB_BANK),
    Banks.VPB: 'http://0.0.0.0:{}/'.format(Ports.VPB_BANK)
}

BankPorts = {
    Banks.VCB: Ports.VCB_BANK,
    Banks.VPB: Ports.VPB_BANK,
}
