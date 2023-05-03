'''
Uses DUO's Python SDK: https://github.com/duosecurity/duo_client_python
Uses the DUO Admin API: https://duo.com/docs/adminapi

Obtains user, authentication and device data from DUO MFA on a specific user
Note: Requires DUO Admin API keys

Created by: jtdepalm@sentara.com
'''

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

INTEGRATION_NAME = "DUO"
SCRIPT_NAME = "DUO Get Users by Name"

@output_handler
def main():
    import duo_client
    import time
    import json
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    result = True
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    try:
        # list to contain results from action
        res = []
        user_id = None
        
        duoApi = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="API Hostname")
        adminSec = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Admin Secret Key")
        adminIntKey = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Admin Integration Key")
        
        # ***parameters***
        # target username to obtain data on
        username = siemplify.extract_action_param("Username", print_value=True)
        # Using SDK. Setup initial authentication.
        admin_api = duo_client.Admin(ikey=adminIntKey, skey=adminSec, host=duoApi)
        # obtain target user's data from DUO
        user_data = admin_api.get_users_by_name(username=username)
        
        for data in user_data:
            user_id = data['user_id']
        
        results = {
            "user_name":username,
            "user_id":user_id,
            "user_data":user_data
        }
        res.append(results)
        siemplify.result.add_result_json(res)
        json_result = json.dumps(res)
        output_message = "Results: {}".format(json_result)
    
    except Exception as e:
        result = False
        status = EXECUTION_STATE_FAILED
        output_message = "Failed. Error is : {}".format(e)




    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Output Message: {}".format(output_message))
    siemplify.LOGGER.info("Result: {}".format(result))
    
    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
