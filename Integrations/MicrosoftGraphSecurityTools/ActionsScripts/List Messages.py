from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from MicrosoftGraphSecurityManager import MicrosoftGraphSecurityManager


@output_handler
def main():
    siemplify = SiemplifyAction()

    client_id = siemplify.extract_configuration_param('Integration',"Client ID")
    secret_id = siemplify.extract_configuration_param('Integration',"Secret ID")
    tenant_id = siemplify.extract_configuration_param('Integration',"Tenant ID")
    certificate_password = siemplify.extract_configuration_param('Integration',"Certificate Password")
    certificate_path = siemplify.extract_configuration_param('Integration',"Certificate Path")
    user_email = siemplify.extract_action_param("User ID", print_value=True)
    filter_select = siemplify.extract_action_param("Select Filter", print_value=True)
    # https://docs.microsoft.com/en-us/graph/query-parameters
    query_parameters =  siemplify.extract_action_param("Query Parameters", print_value=True)
    
    siemplify.LOGGER.info("Connecting to Microsoft Graph Security.")
    mtm = MicrosoftGraphSecurityManager(client_id, secret_id, certificate_path, certificate_password, tenant_id)
    siemplify.LOGGER.info("Connected successfully.")
    
    message_data = mtm.list_messages(user_email, filter_select, query_parameters)
    
    status = EXECUTION_STATE_COMPLETED 
    output_message = "success"
    result_value = "success"
    siemplify.result.add_result_json(message_data)
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)
    
if __name__ == "__main__":
    main()