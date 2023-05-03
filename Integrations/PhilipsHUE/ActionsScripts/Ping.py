from PhilipsManager import PhilipsManager
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import json, requests

# Consts:
INTEGRATION_NAME = "PhilipsHUE"
SCRIPT_NAME = "Ping"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")

    # Extract intgration params:
    bridge_ip = siemplify.extract_configuration_param(INTEGRATION_NAME, "Bridge IP")
    user_name = siemplify.extract_configuration_param(INTEGRATION_NAME, "Authorized Username")

    # Create manager for methods:
    philips_manager = PhilipsManager(bridge_ip, user_name)
    # Init result values:
    status = EXECUTION_STATE_FAILED
    output_message = "The connection failed."
    return_value = False

    try:
        connection_successful = philips_manager.test_connectivity()
        return_value = connection_successful
        output_message = f'Connected successfully to <{bridge_ip}>'

    except:
        siemplify.LOGGER.error(e)
        output_message += " Error: " + str(e)

    finally:
        siemplify.LOGGER.info("----------------- Main - Finished -----------------")
        siemplify.LOGGER.info(
            "status: {}\nresult_value: {}\noutput_message: {}".format(status, return_value, output_message))
        siemplify.end(output_message, return_value, status)


if __name__ == "__main__":
    main()
