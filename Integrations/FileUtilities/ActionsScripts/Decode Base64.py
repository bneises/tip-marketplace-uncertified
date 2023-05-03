from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

import json
import base64

@output_handler
def main():
    siemplify = SiemplifyAction()

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = True  # Set a simple result
    base64_input = siemplify.parameters.get("Base64 Input")
    encoding = siemplify.extract_action_param(param_name="Encoding", is_mandatory=True, print_value=True, default_value='ascii')
    
    try:
        decoded_content = str(base64.b64decode(base64_input), encoding)
        result = {'decoded_content':decoded_content}
        siemplify.result.add_result_json(json.dumps(result))
        output_message = f"Content was succesfully decoded from base 64 to string with encoding {encoding}"
        
    except Exception as e:
        status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        result_value = False


    siemplify.end(output_message, result_value, status)




if __name__ == "__main__":
    main()

