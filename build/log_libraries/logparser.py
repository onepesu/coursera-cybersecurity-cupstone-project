from copy import deepcopy

from utils import ValidationError


def parse_args(argument_list, mapping):
    mapping = deepcopy(mapping)
    parsed_arguments = {}
    accepting_arguments = False
    for argument in argument_list:
        if argument in mapping.keys():
            if mapping[argument].get('is_flag'):
                if accepting_arguments:
                    raise ValidationError('Missing argument')
                key = mapping[argument]['name']
                parsed_arguments[key] = True
                accepting_arguments = False
            elif accepting_arguments is False:
                key = mapping[argument]['name']
                if mapping[argument].get('max_args') is not None:
                    if mapping[argument]['max_args'] == 0:
                        raise ValidationError('Too many {}'.format(argument))
                    mapping[argument]['max_args'] -= 1
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
            raise ValidationError('Unexpected argument')

    if accepting_arguments:
        raise ValidationError('Missing argument')

    return parsed_arguments
