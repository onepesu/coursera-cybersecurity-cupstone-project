from __future__ import print_function

import sys
import json
from bisect import insort
from itertools import izip
from collections import defaultdict


class ValidationError(ValueError):
    pass


def append_to_log(timestamps, employees, guests, filename, encryptor):
    with open(filename, 'w') as opened_file:
        opened_file.write(encryptor.encrypt(json.dumps([
            timestamps, employees, guests
        ]).replace(' ', '')))


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


def change_status(human, history, humans_in, rooms):
    room_id = history[1][-1]
    if room_id >= 0:
        insort(humans_in, human)
        insort(rooms[room_id], human)
    elif room_id == -1:
        insort(humans_in, human)


def print_status(employees, guests):
    rooms = defaultdict(list)
    employees_in = []
    guests_in = []
    for employee, history in employees.iteritems():
        change_status(employee, history, employees_in, rooms)
    print(','.join(employees_in))

    for guest, history in guests.iteritems():
        change_status(guest, history, guests_in, rooms)
    print(','.join(guests_in))

    for room in sorted(rooms.iterkeys()):
        print(str(room) + ': ' + ','.join(rooms[room]))


def print_room_id(arguments, employees, guests):
    if arguments['employee']:
        room_history = employees[arguments['employee'][0]][1]
    else:
        room_history = guests[arguments['guest'][0]][1]
    print(','.join([str(room) for room in room_history if room >= 0]))


def print_total_time(arguments, timestamp, employees, guests):
    if arguments['employee']:
        history = employees[arguments['employee'][0]]
    else:
        history = guests[arguments['guest'][0]]
    if not history:
        sys.exit(0)

    total_time = 0
    in_gallery = False
    for time, position in izip(*history):
        if position == -1 and not in_gallery:
            in_gallery = True
            arrival_time = time
        if position == -2:
            in_gallery = False
            total_time += time - arrival_time
    if in_gallery:
        total_time += timestamp - arrival_time

    print(total_time)


def print_rooms(arguments, employees, guests):
    history = []
    humans = {}
    for employee in arguments['employee']:
        human = 'E' + employee
        humans[human] = -2
        for time, position in izip(*employees[employee]):
            insort(history, [time, position, human])
    for guest in arguments['guest']:
        human = 'G' + guest
        humans[human] = -2
        for time, position in izip(*guests[guest]):
            insort(history, [time, position, human])
    if not history:
        sys.exit(0)

    rooms = set()
    for time, position, human in history:
        humans[human] = position
        if len(set(humans.itervalues())) == 1 and position >= 0:
            rooms.add(str(position))

    print(','.join(sorted(rooms)))
