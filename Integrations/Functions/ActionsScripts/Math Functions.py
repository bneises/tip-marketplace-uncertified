from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

import json

def try_parse_float(s, val=None):
  try:
    number =  float(s)
    return number
  except ValueError:
    return val
    
def try_parse_int(s, val=None):
  try:
    number =  int(s, 10)
    #print(number)
    return number
  except ValueError:
    return val
def _get_int_elements(items):
    numbers = []
    for item in items:
        int_val_after_parse = try_parse_int(item)
        if int_val_after_parse:
            numbers.append(int_val_after_parse)
    return numbers
    
def main():
    siemplify = SiemplifyAction()
    
    numbers_csv_str = siemplify.parameters.get("Numbers", "")
    function = siemplify.parameters.get("Function")

    items = numbers_csv_str.split(',')
    numbers = []
    updated_numbers = []
    for item in items:
        float_val_after_parse = try_parse_float(item)
        int_val_after_parse = try_parse_int(item)
        
        if float_val_after_parse:
            numbers.append(float_val_after_parse)
        elif int_val_after_parse:
            numbers.append(int_val_after_parse)

    output_message = ''
    result = True

    if function == 'Abs':
        for number in numbers:
            updated_number = abs(number)
            updated_numbers.append(updated_number)
        output_message  = '{0} successfully converted to {1} with abs function'.format(numbers,updated_numbers)

    elif function == 'Float':
        for number in numbers:
            updated_number = abs(number)
            updated_numbers.append(updated_number)
        output_message  = '{0} successfully converted to {1} with float function'.format(numbers,updated_numbers)

    elif function == 'Display':
        for number in numbers:
            updated_number = f"{number:,}"
            updated_numbers.append(updated_number)
        output_message = "Successfully converted {0} to {1}".format(numbers,updated_numbers) 

    elif function == 'Hex':
        int_array = _get_int_elements(items)
        for int_item in int_array:
            updated_number = hex(int_item)
            updated_numbers.append(updated_number)
        output_message  = '{0} successfully converted to {1} with hex function'.format(numbers,updated_numbers)

    elif function == 'Int':
        for number in numbers:
            updated_number = int(number)
            updated_numbers.append(updated_number)
        output_message  = '{0} successfully converted to {1} with int function'.format(numbers,updated_numbers)

    elif function == 'Max':
        max_number = max(numbers)
        output_message  = 'Max number in {0} is {1}.'.format(numbers,max_number)
        result = max_number
        
    elif function == 'Min':
        min_number = min(numbers)
        output_message  = 'Min number in {0} is {1}.'.format(numbers,min_number)
        result = min_number

    elif function == 'Round':
        for number in numbers:
            updated_number = round(number)
            updated_numbers.append(updated_number)
        output_message  = '{0} successfully converted to {1} with round function'.format(numbers,updated_numbers)

    elif function == 'Sort':
        updated_numbers = sorted(numbers)
        output_message  = '{0} successfully converted to {1} with sorted function'.format(numbers,updated_numbers)

    elif function == 'Sum':
        sum_array = sum(numbers)
        output_message  = 'Sum of array {0} is {1}.'.format(numbers,sum_array)
        result = sum_array

    siemplify.result.add_result_json(json.dumps(updated_numbers))
    siemplify.result.add_json('Input after {0}'.format(function),json.dumps(updated_numbers))
    

    if(len(updated_numbers) == 1):
        result = updated_numbers[0]
    siemplify.end(output_message, result,EXECUTION_STATE_COMPLETED)




if __name__ == "__main__":
    main()
