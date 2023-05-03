'''
Uses DUO's Python SDK: https://github.com/duosecurity/duo_client_python
Uses the DUO Admin API: https://duo.com/docs/adminapi

Returns Trust Monitor events from the last X days

Note: Requires DUO Admin API keys

Created by: jtdepalm@sentara.com
'''

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

INTEGRATION_NAME = "DUO"
SCRIPT_NAME = "DUO Get Trust Monitor Events"

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
        
        duoApi = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="API Hostname")
        adminSec = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Admin Secret Key")
        adminIntKey = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Admin Integration Key")
        
        # ***parameters***
        # number of days back to obtain DUO Trust Monitor Events
        days_back = int(siemplify.extract_action_param("Number Days Back", print_value=True))
        
        # logic to compute number of days back
        x_days_back = (86400*1000) * days_back
        timestamp_now = int(time.time()*1000)
        timestamp_x_days_ago = timestamp_now - x_days_back
    
        # Using SDK. Setup initial authentication
        admin_api = duo_client.Admin(ikey=adminIntKey, skey=adminSec, host=duoApi)
        # Obtain DUO Trust Mon Events
        trust_monitor = admin_api.get_trust_monitor_events_by_offset(maxtime=timestamp_now, mintime=timestamp_x_days_ago)
        
        
        results = {
            "trust_monitor":trust_monitor
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