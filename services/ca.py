import datetime
import uuid
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class CertificationAuthority(object):
    certificate = None
    prefix = ""

    def __init__(self):
        self.one_day = datetime.timedelta(1, 0, 0)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.builder = x509.CertificateBuilder()

    def create_certificate(self, prefix, common_name, unit_name):
        self.prefix = prefix
        self.builder = self.builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, '{0} {1}'.format(prefix, common_name)),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'{0}'.format(prefix)),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'{0}'.format(unit_name)),
        ]))
        self.builder = self.builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'{0} {1}'.format(prefix, common_name)),
        ]))
        self.builder = self.builder.not_valid_before(datetime.datetime.today() - self.one_day)
        self.builder = self.builder.not_valid_after(datetime.datetime.today() + self.one_day)
        self.builder = self.builder.serial_number(int(uuid.uuid4()))
        self.builder = self.builder.public_key(self.public_key)
        self.builder = self.builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        )
        self.certificate = self.builder.sign(
            private_key=self.private_key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )
        print(isinstance(self.certificate, x509.Certificate))

    def get_private_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(self.prefix.encode())
        )

    def get_public_key(self):
        return self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                            format=serialization.PublicFormat.PKCS1)
