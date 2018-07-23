import base64
import hashlib
import random
import string

from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key=None):
        self.bs = 32
        # self.key = hashlib.sha256(key.encode()).digest()
        self.key = key
        if key is None:
            self.key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        self.key = "LDESBCR17DKG9BY5"   # [76, 68, 69, 83, 66, 67, 82, 49, 55, 68, 75, 71, 57, 66, 89, 53]


    def encrypt(self, raw):
        raw = self._pad(raw)
        # iv = Random.new().read(AES.block_size)
        iv = bytes([235, 59, 203, 149, 32, 90, 98, 114, 16, 202, 210, 84, 77, 180, 162, 68])
        print("IV: ", [i for i in iv])
        cipher = AES.new(self.key, AES.MODE_CBC, iv, segment_size=128)
        return iv+cipher.encrypt(raw)
        # return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        # enc = base64.b64decode(enc)
        print("b64decode: ", [i for i in enc[AES.block_size:]] )
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv, segment_size=128)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


if __name__ == "__main__":
    aes = AESCipher()
    data = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(255))
    print("Data: ", data)
    print ("Key: ", aes.key)
    e = aes.encrypt(data)
    print("Ciphertext: ", [i for i in e])
    print("Ciphertext Type: ",e, type(e[0]))
    # t = aes.decrypt(e)
    iv = [235, 59, 203, 149, 32, 90, 98, 114, 16, 202, 210, 84, 77, 180, 162, 68]
    ciphertext = [146, 118, 217, 85, 115, 100, 151, 37, 177, 148, 124, 16, 180, 131, 81, 69]
    t = aes.decrypt(bytes(iv + ciphertext))
    print("Plaintext: ",t)