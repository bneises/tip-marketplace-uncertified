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
    row_number_str = siemplify.extract_action_param(
        param_name="Row Number", is_mandatory=True
    )
    values_str = siemplify.extract_action_param(param_name="Values", is_mandatory=True)
    sheet_id = siemplify.extract_action_param(param_name="Sheet Id", is_mandatory=True)
    worksheet_name = siemplify.extract_action_param(param_name="Worksheet Name")
    row_number = int(row_number_str)

    try:
        sheet = GoogleSheetFactory(credentials_json).create_spreadsheet(sheet_id)

        if worksheet_name:
            worksheet = sheet.worksheet(worksheet_name)
        else:
            worksheet = sheet.sheet1

        values = values_str.split(",")
        column_num = 1
        for val in values:
            worksheet.update_cell(row_number, column_num, val)
            column_num = column_num + 1

    except Exception as err:
        status = EXECUTION_STATE_FAILED
        message = str(err)
    else:
        status = EXECUTION_STATE_COMPLETED
        message = "The row has been updated successfully"

    siemplify.end(message, status is EXECUTION_STATE_COMPLETED, status)


if __name__ == "__main__":
    main()
