from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_FAILED

from AlertsManager import SixgillEnrichManager, PROVIDER


@output_handler
def main():
    try:
        siemplify = SiemplifyAction()
        siemplify.LOGGER.info('----------------- Main - Param Init -----------------')
        client_id = siemplify.extract_configuration_param(PROVIDER, "Client Id")
        client_secret = siemplify.extract_configuration_param(PROVIDER, "Client Secret")
        siemplify.LOGGER.info('----------------- Main - Started -----------------')
        sixgill_manager = SixgillEnrichManager(client_id, client_secret)
        status, message, result = sixgill_manager.create_sixgill_client()
    except Exception as e:
        message = f"Failed to connect to Cybersixgill... Error is {e}"
        siemplify.LOGGER.error(message)
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result = False
    siemplify.LOGGER.info('----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(f'\n  status: {status}\n  result_value: {result}\n  output_message: {message}')
    siemplify.end(message, result, status)


if __name__ == "__main__":
    main()
