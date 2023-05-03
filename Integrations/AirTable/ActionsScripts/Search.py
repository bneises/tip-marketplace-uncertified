from SiemplifyAction import *
from airtable import Airtable
from airtable.auth import AirtableAuth
import json, sys
from datetime import datetime
from datetime import timedelta

INTEGRATION_NAME = "AirTable"


def main():
    siemplify = SiemplifyAction()
    
    api_key = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME,param_name="Api key")
    base_id = siemplify.parameters["Base id"]
    table_name = siemplify.parameters["Table name"]
    field_name = str(siemplify.parameters["Field name"])
    field_value = str(siemplify.parameters["Field value"])
    max_records_str = str(siemplify.parameters["Max records"])

    max_records = 5

    try:
        max_records = int(max_records_str)
    except ValueError:
        print(max_records_str + " is not an int!")
    

    airtable = Airtable(base_id, table_name, api_key)
    results = airtable.search(field_name, field_value.strip(), maxRecords=max_records)
    
    print(results)

    available_matched_count = len(results)

    siemplify.result.add_result_json(json.dumps(results))
    siemplify.result.add_json("Search Results", json.dumps(results))
    print(json.dumps(results))
    output_message = '{0} records were matched successfully to {1}={2}'.format(available_matched_count, field_name, field_value)
    siemplify.end(output_message, available_matched_count)

if __name__ == "__main__":
    main()