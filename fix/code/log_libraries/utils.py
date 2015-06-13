from __future__ import print_function

import sys
from bisect import insort
from itertools import izip
from collections import defaultdict


class ValidationError(ValueError):
    pass


def get_human_history(arguments, employees, guests):
    if arguments['employee']:
        return employees.get(arguments['employee'][0])
    return guests.get(arguments['guest'][0])


def append_to_log(filename, timestamps, employees, guests, encryptor):
    with open(filename, 'wb') as opened_file:
        opened_file.write(encryptor.encrypt([timestamps, employees, guests]))


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
    history = get_human_history(arguments, employees, guests)
    if history is None:
        room_history = []
    else:
        room_history = history[1]
    print(','.join([str(room) for room in room_history if room >= 0]))


def print_total_time(arguments, timestamp, employees, guests):
    history = get_human_history(arguments, employees, guests)
    if not history:
        print(0)
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
        if employee not in employees:
            return
        human = 'E' + employee
        humans[human] = -2
        for time, position in izip(*employees[employee]):
            insort(history, [time, position, human])
    for guest in arguments['guest']:
        if guest not in guests:
            return
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
            rooms.add(position)

    print(','.join([str(room) for room in sorted(rooms)]))
