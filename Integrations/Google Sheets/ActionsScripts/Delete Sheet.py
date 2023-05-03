from google_sheets import GoogleSheetFactory
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

IDENTIFIER = "Google Sheet"


@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(
        IDENTIFIER, "Credentials Json"
    )
    sheet_id = siemplify.extract_action_param(param_name="Sheet Id", is_mandatory=True)

    try:
        client = GoogleSheetFactory(credentials_json).create_client()
        client.del_spreadsheet(sheet_id)
    except Exception as err:
        status = EXECUTION_STATE_FAILED
        message = str(err)
    else:
        status = EXECUTION_STATE_COMPLETED
        message = "Sheet deleted successfully"
    siemplify.end(message, status is EXECUTION_STATE_COMPLETED, status)


if __name__ == "__main__":
    main()
