class ValidationError(ValueError):
    pass


def parse_args(argument_list, mapping):
    parsed_arguments = {}
    accepting_arguments = False
    for argument in argument_list:
        if argument in mapping.keys():
            if mapping[argument].get('is_flag'):
                key = mapping[argument]['name']
                parsed_arguments[key] = True
                accepting_arguments = False
            else:
                key = mapping[argument]['name']
                if mapping[argument].get('max_args') is not None:
                    if mapping[argument]['max_args'] == 0:
                        raise ValidationError('Too many {}'.format(argument))
                    mapping[argument]['max_args'] -= 1
                accepting_arguments = True
        elif accepting_arguments:
            parsed_arguments[key] = argument
        else:
            raise ValidationError('Unexpected argument')

    if accepting_arguments:
        raise ValidationError('Missing argument')

    return parsed_arguments
