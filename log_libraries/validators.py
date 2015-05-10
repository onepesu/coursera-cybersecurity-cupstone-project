import re
import hashlib

from log_libraries.utils import ValidationError


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
        return True
    try:
        timestamp = int(args['timestamp'][0])
        token = args['token'][0]
    except (KeyError, ValueError, IndexError):
        raise ValidationError("timestamp of wrong type or token doesn't exist")

    if timestamp < 0 or timestamp > 1073741824:
            raise ValidationError('timestamp negative')

    if not is_alphanumeric(token):
            raise ValidationError('token contains invalid characters')

    if args.get('employee'):
        if args.get('guest'):
            raise ValidationError('have both -G and -E')
        human = args.get('employee')[0]
    else:
        if args.get('guest'):
            human = args.get('guest')[0]
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

    return True


def logread_argument_validator(args):
    try:
        token = args['token'][0]
    except (KeyError, IndexError):
        raise ValidationError("There is no token")
    humans = []

    if not is_alphanumeric(token):
            raise ValidationError('token contains invalid characters')

    if args.get('employee'):
        if args.get('guest'):
            raise ValidationError('guest and employee')
        humans = args['employee']
    if args.get('guest'):
        if args.get('employee'):
            raise ValidationError('guest and employee')
        humans = args['guest']

    for human in humans:
        if not is_only_letters(human):
            raise ValidationError('invalid name')

    if args.get('status'):
        if any([args.get('room_id'), args.get('total_time'),
                args.get('rooms')]):
            raise ValidationError('too many parameters')
        if len(humans) != 0:
            raise ValidationError('humans are present')
        return True
    else:
        if not (args.get('employee') or args.get('guest')):
            raise ValidationError('neither employee nor guest')

    if args.get('room_id'):
        if any([args.get('status'), args.get('total_time'),
                args.get('rooms')]):
            raise ValidationError('too many parameters')
        if len(humans) != 1:
            raise ValidationError('only one human allowed')
        try:
            room_id = int(args['room_id'])
        except (ValueError, IndexError):
            raise ValidationError('room id invalid')
        if room_id < 0 or room_id > 1073741824:
            raise ValidationError('room number out of bounds')
    elif args.get('total_time'):
        if any([args.get('room_id'), args.get('status'), args.get('rooms')]):
            raise ValidationError('too many parameters')
        if len(humans) != 1:
            raise ValidationError('only one human allowed')
    elif args.get('rooms'):
        if any([args.get('room_id'), args.get('total_time'),
                args.get('status')]):
            raise ValidationError('too many parameters')
    return True


def token_validator(file_, token):
    with open(file_, 'r') as opened_file:
        encrypted_token = opened_file.read().replace('\n', '')

    supplied_token = hashlib.sha512(token).hexdigest()
    if supplied_token != encrypted_token:
        raise ValidationError('Wrong authentication token')
