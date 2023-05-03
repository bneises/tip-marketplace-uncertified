'''
Uses DUO's Python SDK: https://github.com/duosecurity/duo_client_python

Uses the /check endpoint to verify that the Auth API integration and secret 
keys are valid, and that the signature is being generated properly.

Created by: jtdepalm@sentara.com
'''

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT


INTEGRATION_NAME = "DUO"
SCRIPT_NAME = "DUO API Ping"

@output_handler
def main():
    import duo_client
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    result = True
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    try:
        duoApi = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="API Hostname")
        authSec = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Auth Secret Key")
        authIntKey = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME, param_name="Auth Integration Key")
        # initiate connection to DUO with Auth Keys
        auth_api = duo_client.Auth(ikey=authIntKey, skey=authSec, host=duoApi)
        # Check if Auth Keys are correct
        check = auth_api.check()
        
        # If no exception occur - then connection is successful
        output_message = "Verified Credentials: {}".format(check)
        
    except Exception as e:
        result = False
        status=EXECUTION_STATE_FAILED
        output_message = "Failed to test DUO Auth API Credentials Error is: {}".format(e)
        
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Output Message: {}".format(output_message))
    siemplify.LOGGER.info("Result: {}".format(result))
    
    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
