from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json

from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

@output_handler
def main():
    siemplify = SiemplifyAction()

    
    json_string = siemplify.extract_action_param("Json", print_value=False)
    xpath = siemplify.extract_action_param("JSONPath Expression", print_value=True)
    json_result = {}
    json_result['matches'] = []
    try:
        
        json_data = json.loads(json_string)
        json_expression = parse(xpath)
        
        match = json_expression.find(json_data)
        for m in match:
            json_result['matches'].append(m.value)
        
        
    except Exception as e:
        raise
        

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    
    siemplify.result.add_result_json(json_result)
    siemplify.result.add_json("Json", json_result)



    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
