from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

import json


def try_parse_float_or_int(s, val=None):
    try:
        number = int(s, 10)
        return number
    except ValueError:
        number = float(s)
        return number


def main():
    siemplify = SiemplifyAction()
    
    function = siemplify.parameters.get("Function")

    arg_1_str = siemplify.parameters.get("Arg 1")
    arg_2_str = siemplify.parameters.get("Arg 2")

    arg_1 = try_parse_float_or_int(arg_1_str)
    arg_2 = try_parse_float_or_int(arg_2_str)

    result_value = False
    output_message = 'No function {0} found.'.format(function)
    if function == 'Plus':
        result_value = arg_1 + arg_2; 
        output_message  = '{0} + {1} = {2}'.format(arg_1,arg_2, result_value)

    elif function == 'Sub':
        result_value = arg_1 - arg_2; 
        output_message  = '{0} - {1} = {2}'.format(arg_1,arg_2, result_value)

    elif function == 'Multi':
        result_value = arg_1 * arg_2; 
        output_message  = '{0} * {1} = {2}'.format(arg_1,arg_2, result_value)

    elif function == 'Div':
        result_value = arg_1 / arg_2; 
        output_message  = '{0} / {1} = {2}'.format(arg_1,arg_2, result_value)

    elif function == 'Mod':
        result_value = arg_1 % arg_2; 
        output_message  = '{0} % {1} = {2}'.format(arg_1,arg_2, result_value)

    siemplify.end(output_message, result_value,EXECUTION_STATE_COMPLETED)




if __name__ == "__main__":
    main()
