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
        contents = []
        for line in opened_file.readlines():
            decrypted_line = encryptor.decrypt(line.replace('\n', ''))
            line = json.loads(decrypted_line)
            contents.append(line)
    timestamp, employees, guests = contents[0], contents[1], contents[2]
    if not (isinstance(timestamp, int) or isinstance(employees, dict) or isinstance(guests, dict)):
        raise ValidationError('corrupted file')
    return timestamp, employees, guests

    # supplied_token = hashlib.sha512(token).hexdigest()
    # if supplied_token != encrypted_token:
    #     raise ValidationError('Wrong authentication token')


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
    if timestamp == 0:
        information = employees if status == 'E' else guests
        for visitor, situation in information.items():
            if human == visitor:
                position = situation[0]
                found = True
                break

    future_position = arguments.get('room_id', -1)
    future_action = 'A' if arguments.get('arrival') else 'D'

    allowed_positions = {
        position == -1 and future_position == -1 and future_action == 'D',
        position == -1 and future_position != -1 and future_action == 'A',
        position == -2 and future_position == -1 and future_action == 'A',
        position != -1 and future_position == position and future_action == 'D'
    }

    if not any(allowed_positions):
        raise ValidationError('move not allowed')

    if status == 'E':
        if found:
            new_employees = employees[human][1]
            new_employees.append([time, future_position])
            employees[human] = [future_position, new_employees]
        else:
            employees[human] = [future_position, [time, future_position]]
    elif found:
            new_guests = guests[human][1]
            new_guests.append([time, future_position])
            guests[human] = [future_position, new_guests]
    else:
        guests[human] = [future_position, [time, future_position]]

    return time, employees, guests
