from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import json, re
import base64


@output_handler
def main():
    siemplify = SiemplifyAction()

    input = siemplify.parameters.get("Input")
    function = siemplify.parameters.get("Function")
    param_1 = siemplify.parameters.get("Param 1")
    param_2 = siemplify.parameters.get("Param 2")

    output_message = ''
    result = input

    if function == 'Lower':
        result = input.lower()
        output_message = '{0} successfully converted to {1} with lower function'.format(input, result)

    elif function == 'Upper':
        result = input.upper()
        output_message = '{0} successfully converted to {1} with upper function'.format(input, result)

    elif function == 'Strip':
        result = input.strip()
        output_message = '{0} successfully converted to {1} with strip function'.format(input, result)

    elif function == 'Title':
        result = input.title()
        output_message = '{0} successfully converted to {1} with title function'.format(input, result)

    elif function == 'Count':
        result = input.count(param_1)
        output_message = "'{0}' was found {1} times in '{2}'".format(param_1, result, input)

    elif function == 'Replace':
        result = input.replace(param_1, param_2)
        output_message = '{0} successfully converted to {1} with replace function'.format(input, result)

    elif function == 'Find':
        result = input.find(param_1)
        output_message = "'{0}' was found at index {1} in '{2}'".format(param_1, result, input)

    elif function == 'Upper':
        result = input.upper()
        output_message = '{0} successfully converted to {1} with upper function'.format(input, result)

    elif function == 'IsAlpha':
        result = input.isalpha()
        print(result)
        if (result):
            output_message = "All characters in {0} are alphanumeric".format(input)
        else:
            output_message = "Not all characters in {0} are alphanumeric".format(input)

    elif function == 'IsDigit':
        result = input.isdigit()
        print(result)
        if (result):
            output_message = "All characters in {0} are digits".format(input)
        else:
            output_message = "Not all characters in {0} are digits".format(input)

    elif function == 'Regex Replace':
        result = re.sub(param_1, param_2, input)
        output_message = '{0} successfully converted to {1} with regex replace function'.format(input, result)

    elif function == 'JSON Serialize':
        result = json.dumps(input)
        output_message = "{} successfully serialized to JSON format".format(input)

    elif function == 'Regex':
        if not param_2:
            param_2 = ", "
        result = param_2.join(re.findall(param_1, input))
        output_message = "Found following values:\n{}".format(result)

    elif function == 'DecodeBase64':
        result = (base64.b64decode(input)).decode('utf-8')
        output_message = "Decoded base64 string to: {}".format(result)

    elif function == 'EncodeBase64':
        result = (base64.b64encode(input.encode('utf-8'))).decode('utf-8')
        output_message = "Successfully base64 encoded {}.".format(input)

    elif function == 'RemoveNewLines':
        result = " ".join(input.splitlines())
        output_message = "{0} successfully removed new lines: {1}".format(input, result)

    elif function == 'LogicOperators':
        split_op = ','
        if param_2:
            split_op = param_2
        input_split = [x.strip() for x in input.split(split_op)]
        join_op = " {} ".format(param_1)
        result = join_op.join(input_split)
        output_message = "{0} successfully converted to: {1}".format(input, result)

    elif function == 'Split':
        if param_1:
            split = input.split("{}".format(param_1))
            siemplify.result.add_result_json(json.dumps(split))
            result = str(split)
            output_message = 'Successfully split string {0} with delimiter "{1}"'.format(input, param_1)

        else:
            split = input.split(",")
            siemplify.result.add_result_json(json.dumps(split))
            result = str(split)
            output_message = 'Successfully split string {0} with delimiter ","'.format(input)
    siemplify.end(output_message, result, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
