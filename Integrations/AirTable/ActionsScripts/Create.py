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
    json_fields_str = siemplify.parameters["Json fields"]

    airtable = Airtable(base_id, table_name, api_key)
    output_results = {}
    rows = json.loads(json_fields_str)
    for row in rows:
        res = airtable.insert(row)
        output_results[res['id']] = res['fields']

    output_results_count = len(output_results)
    output_message = '{0} records added successfully to table {1}.'.format(output_results_count,table_name)
    print(output_message)

    siemplify.result.add_result_json(json.dumps(output_results))
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()