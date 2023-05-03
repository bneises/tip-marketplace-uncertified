from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json
import time
from datetime import datetime

GET_USERS_URL = '{}/external/v1/settings/GetUserProfiles'
ACTION_NAME = "GetSiemplifyUsers"
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    
    
    
    hide_disabled = siemplify.parameters.get("Hide Disabled Users").lower() == "true"
    json_payload = {"searchTerm": "",
                    "filterRole": False,
                    "requestedPage": 0,
                    "pageSize": 1000,
                    "shouldHideDisabledUsers": hide_disabled
                    }
    
    siemplify_users = siemplify.session.post(GET_USERS_URL.format(siemplify.API_ROOT), json=json_payload)
    siemplify_users.raise_for_status()
    siemplify.result.add_result_json({"siemplifyUsers":siemplify_users.json()['objectsList']})
    output_message = "Returned Siemplify Users."
    siemplify.end(output_message, True)

if __name__ == "__main__":
    main()