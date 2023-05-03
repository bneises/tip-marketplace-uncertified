from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from AsanaManager import AsanaManager

IDENTIFIER = u"Asana"


@output_handler
def main():
    siemplify = SiemplifyAction()

    personal_access_token = siemplify.extract_configuration_param(IDENTIFIER, "Token")
    base_url = siemplify.extract_configuration_param(IDENTIFIER, "Base URL")

    # Creating an instance of AsanaManager object
    asana_manager = AsanaManager(personal_access_token, base_url)

    # Calling the function test_connectivity() from the AsanaManager
    response = asana_manager.test_connectivity()

    if response:
        return_value = True
        output_message = 'Connected successfully'

    else:
        return_value = False
        output_message = 'The Connection failed'

    # Test connectivity
    siemplify.end(output_message, return_value)


if __name__ == "__main__":
    main()
