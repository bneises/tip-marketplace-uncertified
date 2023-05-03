# CONSTS
OPEN_PH_PARENTHASIS = "{"
CLOSE_PH_PARENTHASIS = "}"
PIPE = "|"
DEBUG = True

#new comment

def print_debug(to_print, function=""):
    if DEBUG:
        print("{} DEBUG: {}".format(function, to_print))

def evaluate_function(val, func_name, func_values):
    if func_name == "default":
        if not val:
            return func_values[0]
        else:
            return val
    elif func_name == "str":
        return str(val)
    elif func_name == "count":
        if not val:
            return "0"
        if isinstance(val, str):
            return "1"
        elif isinstance(val, list):
            return len(val)
        elif isinstance(val, dict):
            return len(val.keys())
        raise Exception("unsupported object: {}".format(val))
    elif func_name == "to_str":
        if isinstance(val, list):
            return ", ".join([str(x) for x in val])
        if isinstance(val, dict):
            return json.dumps(val)
        return str(val)
    elif func_name == "join":
        try:
            delimeter = ",".join(func_values)
            return(delimeter.join([str(x) for x in val]))
        except Exception as e:
            raise Exception(val)
        
    # elif func_name == "ph":
    #     pass
    else:
        raise Exception("Unknown pipe function: {}".format(func_name))


def parse_placeholder(curr_json, placeholder, pipe):
    pipes = [x.strip() for x in placeholder.split(pipe)]
    
    # val = None
    for i, function_str in enumerate(pipes):
        first_split = function_str.strip().split("(")
        if len(first_split) > 2:
            raise Exception("Bad format for pipe function: {}".format(function_str))
        elif len(first_split) == 1:
            # Assuming key_path here
            if isinstance(curr_json, list) or isinstance(curr_json, dict):
                curr_json = find_key_path_in_json(function_str.split("."), curr_json)
            else:
                return None # cant find "keys" in a string
        else: # len is 2
            func_name = first_split[0]
            func_values_string = first_split[1].split(")")[0]
            func_values = [x for x in func_values_string.split(",")]
            curr_json = evaluate_function(curr_json, func_name, func_values)
    
    return curr_json


def parse_raw_message(curr_json, raw_message, pipe=PIPE, open_ph=OPEN_PH_PARENTHASIS, close_ph=CLOSE_PH_PARENTHASIS):
    new_message = ""
    first_break = raw_message.split(open_ph)
    new_message += first_break[0]
    i = 1
    while i < len(first_break):
        second_break = first_break[i].split(close_ph)
        if len(second_break) < 2:
            raise Exception("Missing close PH: '{}'. Raw message {}".format(close_ph, raw_message))
        message_shard = parse_placeholder(curr_json, second_break[0], pipe)
        new_message += str(message_shard) + close_ph.join(second_break[1:])
        i += 1
    
    return new_message
    
def find_key_path_in_json(key_path, json_data):
    """
    Finds the relevant key_path in a json object. 
    If list encountered, this function will return a list of values, one for each 
    match in each of the list's elements (using the rest of the keys)
    """
    return find_key_path_recursive(key_path, json_data)
    
def find_key_path_recursive(key_list, current_json, iteration=0):
    if key_list:
        if isinstance(current_json, list):
            if key_list:
                ret_list = []
                for element in current_json:
                    ret_list.extend(find_key_path_recursive(key_list, element, iteration=iteration+1))
                return ret_list

            return current_json
        if isinstance(current_json, dict):
            if key_list[0] in current_json:
                return find_key_path_recursive(key_list[1:], current_json[key_list[0]], iteration=iteration+1)
            return []
    else:
        if isinstance(current_json, dict):
            return [current_json]
        if isinstance(current_json, list):
            return current_json
        return [u"{}".format(current_json)] # Found val, return it. Format to make everything into string

def GetEntityByString(identifier, entities):
    for ent in entities:
        if identifier.lower() == ent.identifier.lower():
            return ent
    return None


def parse_version_string_to_tuple(version):
    """
    Parse version represented as string to tuple
    :param version: {str} Version represented as string. For example "5.6.1"
    :return: {tuple} Tuple of the version. For example (5,6,1)
    """
    return tuple(map(int, (version.split(u"."))))


def is_supported_siemplify_version(version, min_version):
    """
    Check if Siemplify version is supported
    :param version: {tuple} Tuple representing siemplify version. Example (5,6,1)
    :param min_version: {Tuple} Tuple representing minimum supported siemplify version. Example (5,6,0)
    :return: {bool} True if siemplify version is supported, otherwise False
    """
    return version >= min_version