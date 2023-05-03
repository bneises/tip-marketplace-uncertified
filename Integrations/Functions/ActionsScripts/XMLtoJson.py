from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import xmltodict, json



@output_handler
def main():
    siemplify = SiemplifyAction()

    xml_input = siemplify.extract_action_param("xml", print_value=True)

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = True  # Set a simple result value, used for playbook if\else and placeholders.

    try:
        json_result = xmltodict.parse(xml_input)
        siemplify.result.add_result_json(json_result)
    except Exception as e:
        status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        result_value = False

    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
