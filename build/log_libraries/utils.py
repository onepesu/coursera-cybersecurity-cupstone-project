from __future__ import print_function

import sys
import json
from itertools import chain
from collections import defaultdict

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


def change_status(humans, name, event_type, room_id):
    if event_type == 'A':
        humans[name] = room_id
    elif humans[name] == -1:
        del humans[name]
    else:
        humans[name] = -1


def print_status(arguments, filename):
    history = extract(arguments, filename)
    employers = {}
    guests = {}
    for event in history:
        if event[1] == '':
            change_status(guests, event[2], event[3], event[4])
        else:
            change_status(employers, event[1], event[3], event[4])

    print(','.join(sorted(employers.keys())))
    print(','.join(sorted(guests.keys())))

    rooms = defaultdict(list)
    for human, room in chain(employers.iteritems(), guests.iteritems()):
        rooms[room].append(human)

    for room in sorted(rooms.iterkeys()):
        if room != -1:
            people_in_the_room = sorted(rooms[room])
            print(str(room) + ': ' + ','.join(people_in_the_room))

    sys.exit(0)


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
