import re

from utils import ValidationError


alphanumeric_pattern = re.compile('^[a-zA-Z0-9]+$')
alpha_pattern = re.compile('^[a-zA-Z]+$')
filename_pattern = re.compile('^[a-zA-Z0-9_\.]+$')


def filename_validator(file_):
    if file_ is None or len(file_) > 255 or file_ in ('.', '..') or filename_pattern.search(file_) is None:
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
    with open(file_, 'rb') as opened_file:
        try:
            line = encryptor.decrypt(opened_file.read())
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
        humans = employees
        status = 'E'
    else:
        human = arguments['guest']
        humans = guests
        status = 'G'

    action = 'A' if arguments.get('arrival') else 'D'

    found = False
    position = -2
    if timestamp != 0:
        if human in humans.keys():
            position = humans[human][1][-1]
            found = True

    room_id = arguments['room_id']
    if found is False:
        if action == 'D' or room_id >= 0:
            raise ValidationError('move not allowed')
        humans[human] = [[time], [-1]]
        return time, employees, guests

    if action == 'A':
        if not((position == -1 and room_id >= 0) or
               (position == -2 and room_id == -1)):
            raise ValidationError('move not allowed')
        future_position = room_id
    else:
        if room_id >= 0:
            if position < 0:
                raise ValidationError('move not allowed')
            future_position = -1
        else:
            if position != -1:
                raise ValidationError('move not allowed')
            future_position = -2

    times, positions = humans[human]
    times.append(time)
    positions.append(future_position)

    return time, employees, guests
