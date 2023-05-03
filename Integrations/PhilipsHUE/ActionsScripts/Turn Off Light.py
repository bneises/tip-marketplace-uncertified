from PhilipsManager import PhilipsManager
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

# Consts:
INTEGRATION_NAME = "PhilipsHUE"
SCRIPT_NAME = "Turn Off Light"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")

    # Extract Integration params:
    bridge_ip = siemplify.extract_configuration_param(INTEGRATION_NAME, "Bridge IP")
    username = siemplify.extract_configuration_param(INTEGRATION_NAME, "Authorized Username")

    # Init Action params:
    light_id = siemplify.extract_action_param(param_name="Light ID")

    # Instanciate manager for methods:
    philipsManager = PhilipsManager(bridge_ip, username)

    # Instanciate result json:
    res_json = {}
    res_json["light_id"] = light_id

    # Init action reault values:
    status = EXECUTION_STATE_FAILED
    output_message = "Failed to turn the light off. "
    result_value = False

    try:
        # check ID:
        id_available = philipsManager.search_light_id(light_id)
        if id_available:
            # turn light off:
            res_json["info"] = philipsManager.adjust_light(light_id, False)
            if not res_json.get("info").get("light reachability"):
                output_message += f"Light <{light_id}> is unreachable."
            else:
                status = EXECUTION_STATE_COMPLETED
                output_message = f'Successfully turned the light off on light with id <{light_id}>'
                result_value = True
        else:
            status = EXECUTION_STATE_FAILED
            output_message = f'Light with <{light_id}> does not exist under the bridge <{bridge_ip}>.'
            result_value = False

    except Exception as e:
        siemplify.LOGGER.error(e)
        output_message += "Error: " + str(e)

    finally:
        siemplify.LOGGER.info(
            "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
        siemplify.result.add_result_json(res_json)
        siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
