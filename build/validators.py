import re
import logparser


def validate_file_name(file_name):
    if re.fullmatch('^[a-zA-Z0-9]+', file_name) is None:
            raise logparser.ValidationError('file/log name contains invalid characters')
    return True


def logappend_argument_validator(args, file):
    if args.get('batch_file'):
        if any([args.get('timestamp'), args.get('token'), args.get('employee'), args.get('guest'),
                args.get('arrival'), args.get('departure'), args.get('room_id')]):
            raise logparser.ValidationError('You have a batch file and other args')
        #todo: check that file is a valid name for a file
        validate_file_name(file)
        print('true 1')
        return True
    try:
        timestamp = int(args['timestamp'][0])
        #todo: need to check elsewhere(?) if timestamp increases. Make a global time for each log?

        token = args['token'][0]
        #todo: need to check elsewhere(?) if the log specified, when exists, has this token

    except (KeyError, ValueError, IndexError):
        raise logparser.ValidationError("timestamp of wrong type or token doesn't exist")

    if timestamp < 0:
            raise logparser.ValidationError('timestamp negative')

    if re.fullmatch('^[a-zA-Z0-9]+', token) is None:
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

    if re.fullmatch('^[a-zA-Z]+', human) is None:
        raise logparser.ValidationError('invalid name')

    if args.get('arrival') and args.get('departure'):
        raise logparser.ValidationError('both arrival and departure')

    if args.get('room_id'):
        try:
            room_id = int(args['room_id'][0])
        except (KeyError, ValueError, IndexError):
            raise logparser.ValidationError('room_id is of wrong type')
        if room_id < 0:
            raise logparser.ValidationError('room_id is negative')

    if not file:
        validate_file_name(file)
        raise logparser.ValidationError('log file not valid')
    print('true 2')
    return True
