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

    print(worksheet_name)
    if worksheet_name:
        worksheet = sheet.worksheet(worksheet_name)
    else:
        worksheet = sheet.sheet1

    row_numbers_to_return = []
    cell_list = worksheet.findall(search_value)
    for cell in cell_list:
        if cell.col == column_number_int:
            row_numbers_to_return.append(cell.row)
            values_list = worksheet.row_values(cell.row)
            print(values_list)
    print(row_numbers_to_return)

    output_msg = "."
    output_msg = "Found {0} rows: {1}, with value {2} in column {3}.".format(
        len(values_list), row_numbers_to_return, search_value, column_number_int
    )
    try:
        cell = worksheet.find(search_value)
        row_values = worksheet.row_values(cell.row)
        siemplify.result.add_result_json(row_values)
        ret_val = cell.row
    except gspread.exceptions.CellNotFound:
        output_msg = "Couldn't find row with value {0} in column {1}.".format(
            search_value, column_number_int
        )
        status = EXECUTION_STATE_FAILED
    else:
        status = EXECUTION_STATE_COMPLETED

    siemplify.result.add_result_json(row_numbers_to_return)
    founded_rows = len(row_numbers_to_return)
    siemplify.end(output_msg, founded_rows, status)


if __name__ == "__main__":
    main()
