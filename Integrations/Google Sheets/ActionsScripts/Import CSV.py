import gspread
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
    csv_path = siemplify.extract_action_param(param_name="CSV Path")
    try:
        sheet = GoogleSheetFactory(credentials_json).create_spreadsheet(sheet_id)

        content = open(csv_path, "r").read()

        client = gspread.service_account(filename="./credentials.json")
        client.import_csv(sheet_id, content)

    except Exception as err:
        status = EXECUTION_STATE_FAILED
        message = str(err)
        sheet_id = -1
    else:
        status = EXECUTION_STATE_COMPLETED
        message = "CSV imported successfully"
        sheet_id = sheet.id

    siemplify.end(message, sheet_id, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
