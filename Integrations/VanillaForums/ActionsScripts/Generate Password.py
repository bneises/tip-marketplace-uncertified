from VanillaManager import VanillaManager
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

# Consts:
INTEGRATION_NAME = "VanillaForums"
SCRIPT_NAME = "Generate Password"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")

    # Extract integration params:
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    apiToken = conf.get("API Token")
    baseUrl = conf.get("URL")

    # Extract action params:
    length = int(siemplify.extract_action_param(param_name="Length").strip())
    
    try:
        if length<6:
            raise Exception('Password length must be at least 6 characters')
        siemplify.LOGGER.info("================= Main - Started =================")
        vanillaManager = VanillaManager(apiToken, baseUrl)
        vanilla_pass = vanillaManager.genereate_pass(length)
        
        status = EXECUTION_STATE_COMPLETED
        result_value = vanilla_pass
        output_message = f"Successfully genereated vanilla password of length <{length}>."

    except Exception as e:
        output_message = f'Failed to generate vanilla password. Error: {str(e)}'
        siemplify.LOGGER.error(f'An error occured while generating vanilla password. Error: {str(e)}')
        status = EXECUTION_STATE_FAILED
        result_value = False
        
    finally:
        siemplify.LOGGER.info("----------------- Main - Finished -----------------")
        siemplify.end(output_message, result_value, status)

if __name__ == "__main__":
    main()
