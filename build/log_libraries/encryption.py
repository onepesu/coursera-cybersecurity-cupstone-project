import json
import zlib
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

BS = 32


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    return s[:-ord(s[len(s)-1:])]


class Encrypt(object):
    def __init__(self, key):
        salted = key + hashlib.sha512(key).hexdigest()
        self.key = hashlib.md5(salted).hexdigest()

    def encrypt(self, raw):
        json_obj = json.dumps(raw).replace(' ', '')
        raw = pad(zlib.compress(json_obj))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        to_write = iv + cipher.encrypt(raw)
        return to_write

    def decrypt(self, enc):
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        try:
            unpadded = zlib.decompress(unpad(cipher.decrypt(enc[16:])))
        except zlib.error:
            raise ValueError('bad token')
        return json.loads(unpadded)
