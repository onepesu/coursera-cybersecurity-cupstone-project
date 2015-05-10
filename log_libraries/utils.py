import json
import subprocess
from encryption import Encrypt

LOG_PATH = 'logs'


class ValidationError(ValueError):
    pass


def append_to_log(arguments, filename):
    process = subprocess.Popen(['wc', '-l', filename],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    result, _ = process.communicate()
    lines = result.strip().split()[0]
    encrypt = Encrypt(arguments['token'][0], lines)
    type_ = 'A' if arguments.get('arrival') else 'D'
    room_id = arguments.get('room_id', [None])[0] or 'G'
    plaintext_arguments = json.dumps([
        arguments['timestamp'][0], arguments.get('employee', [''])[0],
        arguments.get('guest', [''])[0], type_, room_id
    ])
    with open(filename, 'a') as opened_file:
        opened_file.write(encrypt.encrypt(plaintext_arguments) + '\n')


def extract(arguments, filename):
    out = []
    with open(filename, 'r') as opened_file:
        for n, line in enumerate(opened_file.readlines()):
            if n == 0:
                continue
            decryptor = Encrypt(arguments['token'][0], n)
            decrypted_line = decryptor.decrypt(line.replace('\n', ''))
            out.append(json.loads(decrypted_line))
    return out

