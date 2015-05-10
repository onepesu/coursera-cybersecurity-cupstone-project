class Encrypt(object):
    def __init__(self, token, salt):
        self.token = token
        self.salt = salt

    def encrypt(self, message):
        encrypted_message = message + self.salt
        return encrypted_message

    def decrypt(self, encrypted_message):
        message = encrypted_message[:-self.salt]
        return message
