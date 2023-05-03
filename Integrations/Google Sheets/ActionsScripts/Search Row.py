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
    column_number_str = siemplify.extract_action_param(
        param_name="Column Number", is_mandatory=True
    )
    search_value = siemplify.extract_action_param(
        param_name="Search value", is_mandatory=True
    )
    sheet_id = siemplify.extract_action_param(param_name="Sheet Id", is_mandatory=True)
    worksheet_name = siemplify.extract_action_param(param_name="Worksheet Name")
    column_number_int = int(column_number_str)

    sheet = GoogleSheetFactory(credentials_json).create_spreadsheet(sheet_id)

    if worksheet_name:
        worksheet = sheet.worksheet(worksheet_name)
    else:
        worksheet = sheet.sheet1

    row_numbers_to_return = []
    ret_val = -1
    output_msg = "."
    try:
        cell = worksheet.find(search_value)
        row_values = worksheet.row_values(cell.row)
        siemplify.result.add_result_json(row_values)
        ret_val = cell.row
        output_msg = "Found row: {0}, with value {1} in column {2}.".format(
            ret_val, search_value, column_number_int
        )

    except gspread.exceptions.CellNotFound:
        output_msg = "Couldn't find row with value {0} in column {1}.".format(
            search_value, column_number_int
        )
        status = EXECUTION_STATE_FAILED
    else:
        status = EXECUTION_STATE_COMPLETED

    siemplify.end(output_msg, ret_val, status)


if __name__ == "__main__":
    main()
