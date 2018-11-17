import base64
import hashlib
import random
import string

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from common.constants import CertificateType, CertificateOwner


class AESCipher(object):

    def __init__(self, key=None):
        self.bs = 32
        # self.key = hashlib.sha256(key.encode()).digest()
        self.key = key
        if key is None:
            self.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        # self.key = "LDESBCR17DKG9BY5"   # [76, 68, 69, 83, 66, 67, 82, 49, 55, 68, 75, 71, 57, 66, 89, 53]


    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        # iv = bytes([235, 59, 203, 149, 32, 90, 98, 114, 16, 202, 210, 84, 77, 180, 162, 68])
        # print("IV: ", [i for i in iv])
        cipher = AES.new(self.key, AES.MODE_CBC, iv, segment_size=128)
        return iv+cipher.encrypt(raw)
        # return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        # enc = base64.b64decode(enc)
        # print("b64decode: ", [i for i in enc[AES.block_size:]] )
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv, segment_size=128)
        # return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def decrypt_aes(key, iv, ciphertext):
    aes = AESCipher(key)
    iv_ds = bytes.fromhex(iv + ciphertext)
    return aes.decrypt(iv_ds)


def encrypt_aes(key, message):
    aes = AESCipher(key)
    return aes.encrypt(message)


def decrypt_rsa(key, ciphertext):
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(ciphertext)
    return message


def encrypt_rsa(key, message):
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(message)
    return ciphertext


def sign_message(priKey, message):
    from Crypto.Signature import PKCS1_PSS
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto import Random

    h = SHA256.new(message)
    signer = PKCS1_PSS.new(priKey, saltLen=20)
    signature = signer.sign(h)
    return signature


def verify_rsa(pubKey, message, signature):
    from Crypto.Signature import PKCS1_PSS
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto import Random

    h = SHA256.new(message)
    verifier = PKCS1_PSS.new(pubKey, saltLen=20)
    if verifier.verify(h, signature):
        return True
    else:
        return False


def ds_check(hashedPart, unhashedPart, ds, k1, iv1, merchant=True):
    pomd_from_ds = decrypt_aes(k1, iv1, ds)
    # hash unhashed
    unhashedPart_hash = SHA256.new(unhashedPart.encode()).hexdigest()
    if merchant:  # Merchant Side
        oipimd = bytes.fromhex(unhashedPart_hash + hashedPart)
    else:
        oipimd = bytes.fromhex(hashedPart + unhashedPart_hash)
    calculated_pomd = SHA256.new(oipimd).hexdigest()
    calculated_pomd = bytes.fromhex(calculated_pomd)
    return calculated_pomd == pomd_from_ds  # pomd_from_ds must be bytes get from decrypt aes


def merchant_decrypt_k1(k1_encrypted):
    from services.keys import get_key
    merchant_key = RSA.importKey(get_key(CertificateOwner.MERCHANT, CertificateType.MERCHANT)['private_key'])
    cipher = PKCS1_OAEP.new(merchant_key)
    k1 = cipher.decrypt(bytes.fromhex(k1_encrypted))
    return k1



if __name__ == "__main__":
#     aes = AESCipher()
#     data = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(255))
#     print("Data: ", data)
#     print ("Key: ", aes.key)
#     e = aes.encrypt(data)
#     print("Ciphertext: ", [i for i in e])
#     print("Ciphertext Type: ", e, type(e[0]))
#     # t = aes.decrypt(e)
#     iv = [235, 59, 203, 149, 32, 90, 98, 114, 16, 202, 210, 84, 77, 180, 162, 68]
#     ciphertext = [146, 118, 217, 85, 115, 100, 151, 37, 177, 148, 124, 16, 180, 131, 81, 69]
#     t = aes.decrypt(bytes(iv + ciphertext))
#     print("Plaintext: ",t)

    pomd = "15aedbab2aa60440a25abee7cfd166d42f6a209d93c9bce8ba19cb5fc67fe409"
    k1 = "a1daafb61e7271ed16f59165a0079d4baeae1e305f10619fc1410d0095827d94"
    iv = "a03307e03dd55bcfc9ab1615c0a0385b"
    aes = AESCipher(k1.encode())
    e = aes.encrypt(pomd)

