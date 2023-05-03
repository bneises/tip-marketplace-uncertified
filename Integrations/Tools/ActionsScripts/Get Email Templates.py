from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json

GET_TEMPLATE_URL = '{}/external/v1/settings/GetEmailTemplateRecords?format=camel'
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.SCRIPT_NAME = "Get Email Templates"

    template_type = siemplify.extract_action_param("Template Type", print_value=True)

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.


    

    
    email_templates = siemplify.session.get(GET_TEMPLATE_URL.format(siemplify.API_ROOT))
    email_templates.raise_for_status()
    res = []
    for template in email_templates.json():
        if template['type'] == 1 and template_type == 'HTML':
            res.append(template)
        elif template['type'] == 0 and template_type == 'Standard':
            res.append(template)
    siemplify.result.add_result_json({"templates":res})
    siemplify.end(output_message, json.dumps(res), status)


if __name__ == "__main__":
    main()
