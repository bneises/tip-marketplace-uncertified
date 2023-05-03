from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

from arcanna_client import *
from constants import GET_JOBS_SCRIPT_NAME


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = GET_JOBS_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    arcanna_url = siemplify.extract_configuration_param('Integration', "Url", is_mandatory=True)
    api_key = siemplify.extract_configuration_param('Integration', "Api Key", is_mandatory=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    status = EXECUTION_STATE_COMPLETED
    output_message = "Get jobs message: "
    result_value = True

    try:
        client = ArcannaClient(api_key=api_key, base_url=arcanna_url, verify=False, proxy=False)
        response_json = client.list_jobs()
        output_message = output_message + f"response: {response_json}"
        siemplify.result.add_result_json(response_json)
    except Exception as e:
        output_message = f'Error executing {GET_JOBS_SCRIPT_NAME}. Reason {e}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False

    siemplify.end(output_message, result_value, status)
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))


if __name__ == "__main__":
    main()
