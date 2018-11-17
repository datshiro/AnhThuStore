from Crypto.PublicKey import RSA

class CertificationAuthority(object):

    def __init__(self):
        self.key = RSA.generate(2048)

    def get_private_key(self):
        return self.key.exportKey()

    def get_public_key(self):
        return self.key.publickey().exportKey()
