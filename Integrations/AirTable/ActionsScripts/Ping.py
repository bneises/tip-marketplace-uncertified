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
    base_id = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME,param_name="Base id")
    table_name = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME,param_name="Table name")


    airtable = Airtable(base_id, table_name, api_key)
    res = airtable.get_all(maxRecords=1)
    siemplify.end('AirTable is connected', True)


if __name__ == "__main__":
    main()