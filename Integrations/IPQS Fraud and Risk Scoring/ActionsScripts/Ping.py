from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from IPQSManager import IPQSManager, PROVIDER


@output_handler
def main():
    siemplify = SiemplifyAction()

    api_key = siemplify.extract_configuration_param(PROVIDER,"API Key")
    data_json = {}
    data_json['email'] = 'support@ipqualityscore.com'
    ipqs_manager = IPQSManager(siemplify, api_key, data_json)
    ipqs_status, ipqs_response = ipqs_manager.query_ipqs('email')
    status = EXECUTION_STATE_COMPLETED
    result = True
    output_message = "Successfully Connected to IPQualityScore"  # human readable message, showed in UI as the action result
    if not ipqs_status: # used to flag back to siemplify system, the action final status
        status = EXECUTION_STATE_FAILED
        result = False
        output_message = f'Error in connecting to IPQualityScore. Reason: {ipqs_response["message"]}'
        
    result_value = result  # Set a simple result value, used for playbook if\else and placeholders.
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
