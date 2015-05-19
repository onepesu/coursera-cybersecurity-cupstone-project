import re
import json
import hashlib
import os.path
from log_libraries import utils

from utils import ValidationError


alphanumeric_pattern = re.compile('^[a-zA-Z0-9]+$')
alpha_pattern = re.compile('^[a-zA-Z]+$')


def filename_validator(file_):
    if re.search('^[a-zA-Z0-9_]+$', file_) is None:
        raise ValidationError('filename not valid')


def is_alphanumeric(token):
    return alphanumeric_pattern.search(token) is not None


def is_only_letters(name):
    return alpha_pattern.search(name) is not None


def validate_integer_list(integer_list, lower_bound=1, upper_bound=1073741823):
    for integer in integer_list:
        try:
            integer = int(integer)
        except ValueError:
            raise ValidationError('integer not an int')
        if integer < lower_bound or integer > upper_bound:
            raise ValidationError('integer out of bounds')

    return int(integer_list[-1])


def logappend_argument_validator(args):
    if args.get('batch_file'):
        if len(args) > 1:
            raise ValidationError('You have a batch file and other args')
        return
    try:
        timestamp = validate_integer_list(args['timestamp'])
        token = args['token'][-1]
    except KeyError:
        raise ValidationError("timestamp of wrong type or token doesn't exist")

    args['timestamp'] = timestamp

    if not is_alphanumeric(token):
        raise ValidationError('token contains invalid characters')
    args['token'] = token

    if args.get('employee'):
        if args.get('guest'):
            raise ValidationError('have both -G and -E')
        human = args.get('employee')[-1]
        args['employee'] = human
        args['guest'] = ""
    else:
        if args.get('guest'):
            human = args.get('guest')[-1]
            args['guest'] = human
            args['employee'] = ""
        else:
            raise ValidationError('Neither -E or -G')

    if not is_only_letters(human):
        raise ValidationError('invalid human name')

    if not (bool(args.get('arrival')) ^ bool(args.get('departure'))):
        raise ValidationError('not arrival xor departure')

    try:
        args['room_id'] = validate_integer_list(args['room_id'], lower_bound=0)
    except KeyError:
        args['room_id'] = -1


def logread_argument_validator(args):
    try:
        token = args['token'][-1]
    except KeyError:
        raise ValidationError("There is no token")

    if not is_alphanumeric(token):
            raise ValidationError('token contains invalid characters')
    args['token'] = token

    args['employee'] = args.get('employee', [])
    args['guest'] = args.get('guest', [])

    employees, guests = len(args['employee']), len(args['guest'])

    for human in args['employee'] + args['guest']:
        if not is_only_letters(human):
            raise ValidationError('invalid name')

    if args.get('status'):
        if any([args.get('room_id'), args.get('total_time'),
                args.get('rooms')]):
            raise ValidationError('too many parameters')
        if employees + guests != 0:
            raise ValidationError('humans are present')
        return
    else:
        if employees + guests == 0:
            raise ValidationError('neither employee nor guest')

    if args.get('room_id'):
        if any([args.get('total_time'), args.get('rooms')]):
            raise ValidationError('too many parameters')
        if employees + guests != 1:
            raise ValidationError('only one human allowed')

    elif args.get('total_time'):
        if args.get('rooms'):
            raise ValidationError('too many parameters')
        if employees + guests != 1:
            raise ValidationError('only one human allowed')
    else:
        try:
            args['rooms']
        except KeyError:
            raise ValidationError('too few parameters')


def token_validator(file_, encryptor):
    with open(file_, 'r') as opened_file:
        lines = opened_file.readlines()
        if len(lines) != 1:
            raise ValidationError('corrupted file')
        try:
            decrypted_line = encryptor.decrypt(lines[0])
            line = json.loads(decrypted_line)
        except ValueError:
            raise ValidationError('corrupted file')

    try:
        timestamp, employees, guests = line
    except (ValueError, TypeError):
        raise ValidationError('corrupted file')

    return timestamp, employees, guests


def context_validator(arguments, timestamp, employees, guests):
    time = arguments['timestamp']

    if time <= timestamp:
        raise ValidationError('This time has passed')

    if arguments.get('employee'):
        human = arguments['employee']
        status = 'E'
    else:
        human = arguments['guest']
        status = 'G'

    found = False
    position = -2
    if timestamp != 0:
        information = employees if status == 'E' else guests
        for visitor, situation in information.items():
            if human == visitor:
                position = situation[0]
                found = True
                break

    action = 'A' if arguments.get('arrival') else 'D'
    if action == 'A':
        future_position = arguments.get('room_id', -1)
    else:
        if arguments.get('room_id') >= 0:
            future_position = -1
        else:
            future_position = -2

    allowed_positions = {
        position == -1 and future_position == -2 and action == 'D',
        position == -1 and future_position >= 0 and action == 'A',
        position == -2 and future_position == -1 and action == 'A',
        position >= 0 and future_position == -1 and action == 'D'
    }

    if not any(allowed_positions):
        raise ValidationError('move not allowed')

    if status == 'E':
        if found:
            new_employees = employees[human][1]
            new_employees.append([time, future_position])
            employees[human] = [future_position, new_employees]
        else:
            employees[human] = [future_position, [[time, future_position]]]
    elif found:
            new_guests = guests[human][1]
            new_guests.append([time, future_position])
            guests[human] = [future_position, new_guests]
    else:
        guests[human] = [future_position, [[time, future_position]]]

    return time, employees, guests
