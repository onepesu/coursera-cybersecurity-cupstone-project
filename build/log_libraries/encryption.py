class Encrypt(object):
    def __init__(self, token):
        self.token = token

    def encrypt(self, message):
        encrypted_message = message + self.token
        return encrypted_message

    def decrypt(self, encrypted_message):
        message = encrypted_message[:-len(self.token)]
        return message
