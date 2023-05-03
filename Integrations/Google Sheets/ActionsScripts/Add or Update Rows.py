import json

import gspread
from google_sheets import GoogleSheetFactory
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

IDENTIFIER = "Google Sheet"


def add_or_update_row(
    siemplify,
    worksheet,
    field_name,
    column_number_int,
    values_dict,
    start_column,
    end_column,
    count,
):
    ret_val = {"row_number": -1, "output_message": ""}
    row_index = -1
    value_to_search = values_dict
    row_values_list = list(values_dict.values())

    try:
        cell = worksheet.find(str(value_to_search))
        if cell.col == column_number_int:
            siemplify.result.add_result_json(values_dict)
            row_index = cell.row
            output_msg = "Found row: {0}, with value {1} in column {2}.".format(
                row_index, field_name, column_number_int
            )
    except gspread.exceptions.CellNotFound:
        output_msg = "The cell was not found"
    except Exception as err:
        output_msg = "Unexpected error: {}".format(err)
    finally:
        print(output_msg)

    updated_range = ""
    if row_index != -1:
        updated_range = "{0}{1}:{2}{1}".format(
            start_column, row_index + count, end_column
        )
        worksheet.update(updated_range, [row_values_list])
        output_msg = "Updated range {0} with values {1}.".format(
            updated_range, row_values_list
        )

    else:
        res = worksheet.append_row(row_values_list)
        updated_range = res["updates"]["updatedRange"]

        output_msg = "Added new row in {0} with values {1}.".format(
            updated_range, row_values_list
        )

    print(updated_range)
    ret_val["updated_range"] = updated_range
    ret_val["output_message"] = output_msg
    return ret_val


@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(
        IDENTIFIER, "Credentials Json"
    )
    column_number_str = siemplify.extract_action_param(
        param_name="Column Number", is_mandatory=True
    )
    column_header = siemplify.extract_action_param(
        param_name="Field Name", is_mandatory=True
    )
    sheet_id = siemplify.extract_action_param(param_name="Sheet Id", is_mandatory=True)
    worksheet_name = siemplify.extract_action_param(param_name="Worksheet Name")
    start_column = siemplify.extract_action_param(param_name="Start Column")
    end_column = siemplify.extract_action_param(param_name="End Column")

    column_number_int = int(column_number_str)
    json_fields_str = siemplify.extract_action_param(param_name="Json")
    rows = json.loads(json_fields_str)

    updated_rows = []
    try:
        sheet = GoogleSheetFactory(credentials_json).create_spreadsheet(sheet_id)

        if worksheet_name:
            worksheet = sheet.worksheet(worksheet_name)
        else:
            worksheet = sheet.sheet1

        count = 0
        for row in rows:
            ret_val = add_or_update_row(
                siemplify,
                worksheet,
                column_header,
                column_number_int,
                row,
                start_column,
                end_column,
                count,
            )
            count = count + 1
            updated_rows.append(ret_val["updated_range"])
    except Exception as err:
        message = str(err)
        status = EXECUTION_STATE_FAILED
    else:
        message = "{0} rows were updated or added.".format(len(updated_rows))
        status = EXECUTION_STATE_COMPLETED

    siemplify.end(message, len(updated_rows), status)


if __name__ == "__main__":
    main()
