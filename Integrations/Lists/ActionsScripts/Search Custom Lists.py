from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

CUSTOM_LIST_ENDPOINT = "{}/external/v1/settings/GetTrackingListRecords"


def get_custom_list_records(siemplify):
    
    url = CUSTOM_LIST_ENDPOINT.format(siemplify.API_ROOT)
    records = siemplify.session.get(url)
    siemplify.validate_siemplify_error(records)
    
    return records.json()


@output_handler
def main():
    siemplify = SiemplifyAction()

    categories = siemplify.extract_action_param("Categories", print_value=True, default_value=None)
    string = siemplify.extract_action_param("String to Search", print_value=True, default_value=None)
    
    list_categories = [category.strip() for category in categories.split(",") if category.strip()] if categories else []
    status = EXECUTION_STATE_COMPLETED 
    output_message = "Failed to get custom list items with provided parameters." 
    result_value = True 

    
    siemplify.LOGGER.info('----------------- Main - Started -----------------')


    try:
        siemplify.LOGGER.info(f"Getting custom list records")
        records = get_custom_list_records(siemplify)
        
        siemplify.LOGGER.info(f"Searching records for match criteria")
        if list_categories:
            relevant_records = []
            for record in records:
                if record["category"] in list_categories:
                    relevant_records.append(record)
        else:
            relevant_records = records
        
        json_result = []
        match_records = []
        if relevant_records:
            if string:
                for record in relevant_records:
                    if string in record["entityIdentifier"]:
                        match_records.append(record)
            else:
                match_records = relevant_records
        if match_records:
            siemplify.LOGGER.info(f"Found {len(match_records)} matching records")
            json_result= match_records
        else:
            siemplify.LOGGER.info(f"No matching records found")
            result_value = False
            
        if json_result:
            siemplify.result.add_result_json(json_result)
            output_message = f"Found {len(match_records)} matching records"
    except Exception as e:
        status = EXECUTION_STATE_FAILED
        result_value = False
        output_message = f"Failed to find records in custom lists"
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
        


    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
