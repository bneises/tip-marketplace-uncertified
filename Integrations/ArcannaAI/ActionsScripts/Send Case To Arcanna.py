from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from arcanna_client import *

from constants import SEND_CASE_SCRIPT_NAME


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SEND_CASE_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    arcanna_url = siemplify.extract_configuration_param('Integration', "Url", is_mandatory=True)
    api_key = siemplify.extract_configuration_param('Integration', "Api Key", is_mandatory=True)
    job_id = int(siemplify.extract_action_param("Job Id", print_value=True, is_mandatory=True))
    username = siemplify.extract_action_param("Username", print_value=True, is_mandatory=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    full_case = siemplify._get_case()
    status = EXECUTION_STATE_COMPLETED
    output_message = "output message :"
    result_value = None
    
    if full_case is None:
        status = EXECUTION_STATE_FAILED
        output_message = "No case details returned"
        result_value = False
        siemplify.end(output_message, result_value, status)

    try:
        client = ArcannaClient(api_key=api_key, base_url=arcanna_url, verify=False, proxy=False)
        severity = 0
        title = full_case.get("title")
        target_entities = siemplify.context_data.get("target_entities")
        raw_payload = full_case
        raw_payload["siemplify_username"] = username
        raw_payload["target_entities"] = target_entities
        response_json = client.send_raw_event(job_id=job_id, severity=severity, title=title, raw_body=raw_payload)
        result_value = True
        output_message = output_message + f"response={response_json}"
        siemplify.result.add_result_json(response_json)
    except Exception as e:
        output_message = f'Error executing {SEND_CASE_SCRIPT_NAME}. Reason {e}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.end(output_message, result_value, status)
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))


if __name__ == "__main__":
    main()
