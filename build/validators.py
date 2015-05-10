import re
import hashlib
import logparser


alphanumeric_pattern = re.compile('^[a-zA-Z0-9]+')
alpha_pattern = re.compile('^[a-zA-Z]+')


def filename_validator(file):
    if re.fullmatch('^[a-zA-Z0-9_]+', file) is None:
        raise logparser.ValidationError('filename not valid')


def is_alphanumeric(token):
    return alphanumeric_pattern.fullmatch(token) is not None


def is_only_letters(name):
    return alpha_pattern.fullmatch(name) is not None


def logappend_argument_validator(args):
    if args.get('batch_file'):
        if any([args.get('timestamp'), args.get('token'), args.get('employee'), args.get('guest'),
                args.get('arrival'), args.get('departure'), args.get('room_id')]):
            raise logparser.ValidationError('You have a batch file and other args')
        print('true 1')
        return True
    try:
        timestamp = int(args['timestamp'][0])
        token = args['token'][0]
    except (KeyError, ValueError, IndexError):
        raise logparser.ValidationError("timestamp of wrong type or token doesn't exist")

    if timestamp < 0 or timestamp > 2147483647:
            raise logparser.ValidationError('timestamp negative')

    if not is_alphanumeric(token):
            raise logparser.ValidationError('token contains invalid characters')

    if args.get('employee'):
        if args.get('guest'):
            raise logparser.ValidationError('have both -G and -E')
        human = args.get('employee')[0]
    else:
        if args.get('guest'):
            human = args.get('guest')[0]
        else:
            raise logparser.ValidationError('Neither -E or -G')

    if not is_only_letters(human):
        raise logparser.ValidationError('invalid human name')

    # todo: make the next two checks a xor
    if args.get('arrival') and args.get('departure'):
        raise logparser.ValidationError('both arrival and departure')

    if not (args.get('arrival') or args.get('departure')):
        raise logparser.ValidationError('neither arrival nor departure')

    if args.get('room_id'):
        try:
            room_id = int(args['room_id'][0])
        except (KeyError, ValueError, IndexError):
            raise logparser.ValidationError('room_id is of wrong type')
        if room_id < 0 or room_id > 2147483647:
            raise logparser.ValidationError('room_id is negative')

    print('true 2')
    return True


def logread_argument_validator(args):
    try:
        token = args['token'][0]
    except (KeyError, IndexError):
        raise logparser.ValidationError("There is no token")
    humans = []

    if not is_alphanumeric(token):
            raise logparser.ValidationError('token contains invalid characters')

    if args.get('employee'):
        if args.get('guest'):
            raise logparser.ValidationError('guest and employee')
        humans = args['employee']
    if args.get('guest'):
        if args.get('employee'):
            raise logparser.ValidationError('guest and employee')
        humans = args['guest']

    for human in humans:
        if not is_only_letters(human):
            raise logparser.ValidationError('invalid name')

    if args.get('status'):
        if any([args.get('room_id'), args.get('total_time'),args.get('rooms')]):
            raise logparser.ValidationError('too many parameters')
        if len(humans) != 0:
            raise logparser.ValidationError('humans are present')
        print('fine -S')
        return True
    else:
        if not (args.get('employee') or args.get('guest')):
            raise logparser.ValidationError('neither employee nor guest')

    if args.get('room_id'):
        if any([args.get('status'), args.get('total_time'), args.get('rooms')]):
            raise logparser.ValidationError('too many parameters')
        if len(humans) != 1:
            raise logparser.ValidationError('only one human allowed')
    elif args.get('total_time'):
        if any([args.get('room_id'), args.get('status'), args.get('rooms')]):
            raise logparser.ValidationError('too many parameters')
        if len(humans) != 1:
            raise logparser.ValidationError('only one human allowed')
    elif args.get('rooms'):
        if any([args.get('room_id'), args.get('total_time'), args.get('status')]):
            raise logparser.ValidationError('too many parameters')
    print('all fine')
    return True


def token_validator(file, token):
    with open(file, 'r') as opened_file:
        encrypted_token = opened_file.read().replace('\n', '')

    supplied_token = hashlib.sha512(bytes(token, 'utf-8')).hexdigest()
    if supplied_token != encrypted_token:
        raise logparser.ValidationError('Wrong authentication token')
