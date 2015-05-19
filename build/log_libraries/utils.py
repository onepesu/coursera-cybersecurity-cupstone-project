from __future__ import print_function

import sys
import json
from itertools import chain
from collections import defaultdict


class ValidationError(ValueError):
    pass


def append_to_log(timestamps, employees, guests, filename, encryptor):
    with open(filename, 'w') as opened_file:
        opened_file.write(encryptor.encrypt(json.dumps([
            timestamps, employees, guests
        ])))


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


def print_status(employees, guests):
    print(','.join(sorted([employee for employee, history in employees.items()
                           if history[0] != -2])))
    print(','.join(sorted([guest for guest, history in guests.items()
                           if history[0] != -2])))

    rooms = defaultdict(list)
    for human, history in chain(employees.iteritems(), guests.iteritems()):
        room_id = history[0]
        if room_id >= 0:
            rooms[room_id].append(human)

    for room in sorted(rooms.iterkeys()):
        people_in_the_room = sorted(rooms[room])
        print(str(room) + ': ' + ','.join(people_in_the_room))


def print_room_id(arguments, employees, guests):
    if arguments['employee']:
        history = employees[arguments['employee'][0]][1]
    else:
        history = guests[arguments['guest'][0]][1]
    rooms = []
    for event in history:
        room = event[1]
        if room >= 0:
            rooms.append(str(room))
    print(','.join(rooms))


def print_total_time(arguments, timestamp, employees, guests):
    if arguments['employee']:
        history = employees[arguments['employee'][0]][1]
    else:
        history = guests[arguments['guest'][0]][1]
    if not history:
        sys.exit(0)

    total_time = 0
    in_gallery = False
    for event in history:
        if event[1] == -1 and not in_gallery:
            in_gallery = True
            arrival_time = event[0]
        if event[-1] == -2:
            in_gallery = False
            total_time += event[0] - arrival_time
    if in_gallery:
        total_time += timestamp - arrival_time

    print(total_time)


def print_rooms(arguments, employees, guests):
    history = []
    humans = {}
    for employee in arguments['employee']:
        human = 'E' + employee
        humans[human] = -2
        for event in employees[employee][1]:
            history.append(event + [human])
    for guest in arguments['guest']:
        human = 'G' + guest
        humans[human] = -2
        for event in guests[guest][1]:
            history.append(event + [human])
    if not history:
        sys.exit(0)

    rooms = set()
    for event in sorted(history):
        human = event[2]
        room_id = event[1]
        humans[human] = room_id
        if len(set(humans.itervalues())) == 1 and room_id >= 0:
            rooms.add(str(room_id))

    print(','.join(sorted(rooms)))
