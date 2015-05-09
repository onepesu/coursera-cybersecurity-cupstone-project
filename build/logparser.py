class ValidationError(ValueError):
    pass


def parse_args(argument_list, mapping):
    parsed_arguments = {}
    active_key = None
    for argument in argument_list:
        if argument in mapping.keys():
            if mapping[argument].get('is_flag'):
                flag_key = mapping[argument]['name']
                parsed_arguments[flag_key] = True
            else:
                active_key = mapping[argument]['name']
        else:
            parsed_arguments[active_key] = argument

    return parsed_arguments
