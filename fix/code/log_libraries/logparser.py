from copy import deepcopy

from utils import ValidationError


def parse_args(argument_list, mapping):
    mapping = deepcopy(mapping)
    parsed_arguments = {}
    file_ = None
    argument_list = argument_list
    accepting_arguments = False
    for argument in argument_list:
        if argument == '':
            continue
        if argument in mapping.keys():
            if mapping[argument].get('is_flag'):
                if accepting_arguments:
                    raise ValidationError('Missing argument')
                key = mapping[argument]['name']
                parsed_arguments[key] = True
                accepting_arguments = False
            elif accepting_arguments is False:
                key = mapping[argument]['name']
                accepting_arguments = True
            else:
                raise ValidationError('Missing argument')
        elif accepting_arguments:
            try:
                parsed_arguments[key].append(argument)
            except KeyError:
                parsed_arguments[key] = [argument]
            accepting_arguments = False
        else:
            if file_ is None:
                file_ = argument
            else:
                raise ValidationError('Unexpected argument')

    if accepting_arguments or file_ is None:
        raise ValidationError('Missing argument')

    return parsed_arguments, file_
