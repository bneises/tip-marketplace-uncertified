from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

import time
from constants import AWAIT_ARCANNA_INFERENCE_SCRIPT_NAME


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = AWAIT_ARCANNA_INFERENCE_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    period = siemplify.extract_action_param("Period", print_value=True, is_mandatory=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    status = EXECUTION_STATE_COMPLETED
    output_message = "Awaited Arcanna Inference"
    result_value = True
    try:
        siemplify.LOGGER.info(f"Arcanna Period ={period}")

        time.sleep(int(period))
    except Exception as e:
        output_message = f'Error executing {AWAIT_ARCANNA_INFERENCE_SCRIPT_NAME}. Reason {e}'
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = False
    siemplify.end(output_message, result_value, status)

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))


if __name__ == "__main__":
    main()
