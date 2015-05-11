import sys
import json
from encryption import Encrypt

LOG_PATH = 'logs'


class ValidationError(ValueError):
    pass


def append_to_log(arguments, filename):
    encryptor = Encrypt(arguments['token'])
    type_ = 'A' if arguments.get('arrival') else 'D'
    room_id = arguments['room_id']
    plaintext_arguments = json.dumps([
        arguments['timestamp'], arguments['employee'],
        arguments['guest'], type_, room_id
    ])
    with open(filename, 'a') as opened_file:
        opened_file.write(encryptor.encrypt(plaintext_arguments) + '\n')


def extract(arguments, filename, filtering=False):
    out = []
    decryptor = Encrypt(arguments['token'])
    guest_list = arguments['guest']
    employee_list = arguments['employee']
    with open(filename, 'r') as opened_file:
        for n, line in enumerate(opened_file.readlines()):
            if n == 0:
                continue
            decrypted_line = decryptor.decrypt(line.replace('\n', ''))
            line = json.loads(decrypted_line)
            if filtering:
                if line[1] not in employee_list and line[2] not in guest_list:
                    continue
            out.append(line)
    return out


def print_status(arguments, filename):
    print(extract(arguments, filename))


def print_room_id(arguments, filename):
    history = extract(arguments, filename, filtering=True)
    rooms = []
    for event in history:
        room = event[-1]
        if room != -1 and event[-2] == 'A':
            rooms.append(str(room))
    print(','.join(rooms))
    sys.exit(0)


def print_total_time(arguments, filename):
    print(extract(arguments, filename, filtering=True))


def print_rooms(arguments, filename):
    print(extract(arguments, filename, filtering=True))
