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
    room_id = arguments.get('room_id') or 'G'
    plaintext_arguments = json.dumps([
        arguments['timestamp'][0], arguments.get('employee', [''])[0],
        arguments.get('guest', [''])[0], type_, room_id
    ])
    with open(filename, 'a') as opened_file:
        opened_file.write(encrypt.encrypt(plaintext_arguments) + '\n')
