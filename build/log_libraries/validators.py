import re
import hashlib

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


def logappend_argument_validator(args):
    if args.get('batch_file'):
        if any([args.get('timestamp'), args.get('token'), args.get('employee'),
                args.get('guest'), args.get('arrival'), args.get('departure'),
                args.get('room_id')]):
            raise ValidationError('You have a batch file and other args')
        return
    try:
        timestamp = int(args['timestamp'][0])
        token = args['token'][0]
    except (KeyError, ValueError, IndexError):
        raise ValidationError("timestamp of wrong type or token doesn't exist")

    if timestamp < 0 or timestamp > 1073741824:
            raise ValidationError('timestamp negative')
    args['timestamp'] = timestamp

    if not is_alphanumeric(token):
            raise ValidationError('token contains invalid characters')
    args['token'] = token

    if args.get('employee'):
        if args.get('guest'):
            raise ValidationError('have both -G and -E')
        human = args.get('employee')[0]
        args['employee'] = human
        args['guest'] = ""
    else:
        if args.get('guest'):
            human = args.get('guest')[0]
            args['guest'] = human
            args['employee'] = ""
        else:
            raise ValidationError('Neither -E or -G')

    if not is_only_letters(human):
        raise ValidationError('invalid human name')

    # todo: make the next two checks a xor
    if args.get('arrival') and args.get('departure'):
        raise ValidationError('both arrival and departure')

    if not (args.get('arrival') or args.get('departure')):
        raise ValidationError('neither arrival nor departure')

    if args.get('room_id'):
        try:
            room_id = int(args['room_id'][0])
        except (KeyError, ValueError, IndexError):
            raise ValidationError('room_id is of wrong type')
        if room_id < 0 or room_id > 1073741824:
            raise ValidationError('room_id is negative')
        args['room_id'] = room_id
    else:
        args['room_id'] = -1


def logread_argument_validator(args):
    try:
        token = args['token'][0]
    except (KeyError, IndexError):
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


def token_validator(file_, token):
    with open(file_, 'r') as opened_file:
        encrypted_token = opened_file.readline().replace('\n', '')

    supplied_token = hashlib.sha512(token).hexdigest()
    if supplied_token != encrypted_token:
        raise ValidationError('Wrong authentication token')


def context_validator(arguments, filename):
    pass
