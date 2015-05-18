from __future__ import print_function

import sys
import json
from itertools import chain
from collections import defaultdict


class ValidationError(ValueError):
    pass


def append_to_log(arguments, filename, encryptor):
    type_ = 'A' if arguments.get('arrival') else 'D'
    room_id = arguments['room_id']
    plaintext_arguments = json.dumps([
        arguments['timestamp'], arguments['employee'],
        arguments['guest'], type_, room_id
    ])
    with open(filename, 'a') as opened_file:
        opened_file.write(encryptor.encrypt(plaintext_arguments) + '\n')


def extract(arguments, filename, decryptor, filtering=False):
    out = []
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


def extract_for_append(arguments, filename, decryptor):
    human = arguments['guest'] or arguments['employee']
    last_line = []
    status = ''
    position = -2
    previous = ''
    with open(filename, 'r') as opened_file:
        for n, line in enumerate(opened_file.readlines()):
            if n == 0:
                continue
            decrypted_line = decryptor.decrypt(line.replace('\n', ''))
            line = json.loads(decrypted_line)
            last_line = line
            if line[1] != human and line[2] != human:
                    continue
            previous = line[3]
            if line[1] == human:
                status = 'E'
            else:
                status = 'G'
            position = line[-1]
    time = last_line[0]

    return [time, status, position, previous]


def change_status(humans, name, event_type, room_id):
    if event_type == 'A':
        humans[name] = room_id
    elif humans[name] == -1:
        del humans[name]
    else:
        humans[name] = -1


def print_status(arguments, filename, encryptor):
    history = extract(arguments, filename, encryptor)
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


def print_room_id(arguments, filename, encryptor):
    history = extract(arguments, filename, encryptor, filtering=True)
    rooms = []
    for event in history:
        room = event[-1]
        if room != -1 and event[-2] == 'A':
            rooms.append(str(room))
    print(','.join(rooms))
    sys.exit(0)


def print_total_time(arguments, filename, encryptor):
    history = extract(arguments, filename, encryptor, filtering=True)
    if not history:
        sys.exit(0)
    total_time = 0
    in_gallery = False
    for event in history:
        if event[-1] == -1 and event[-2] == 'A':
            in_gallery = True
            arrival_time = event[0]
        if event[-1] == -1 and event[-2] == 'L':
            in_gallery = False
            total_time += event[0] - arrival_time
    if in_gallery:
        total_time += history[-1][0] - arrival_time

    print(total_time)
    sys.exit(0)


def print_rooms(arguments, filename, encryptor):
    history = extract(arguments, filename, encryptor, filtering=True)
    if not history:
        sys.exit(0)
    rooms = set()
    humans = {
        human: -2 for human in arguments['guest'] + arguments['employee']
    }
    for event in history:
        human = event[1] or event[2]
        room_id = event[-1]
        if event[-2] == 'A':
            humans[human] = room_id
            if len(set(humans.itervalues())) == 1 and room_id >= 0:
                rooms.add(str(room_id))
        elif room_id == -1:
            humans[human] = -2
        else:
            humans[human] = -1

    print(','.join(sorted(rooms)))
    sys.exit(0)
