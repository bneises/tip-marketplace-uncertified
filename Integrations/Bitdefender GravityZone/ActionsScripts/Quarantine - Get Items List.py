from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from BitdefenderGravityZoneManager import BitdefenderGravityZoneManager

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    api_key = siemplify.extract_configuration_param('Integration',"API Key")
    access_url = siemplify.extract_configuration_param('Integration',"Access URL")
    verify_ssl = siemplify.extract_configuration_param('Integration',"Verify SSL", input_type=bool)
    endpoint_id = siemplify.extract_action_param("Endpoint ID", print_value=True)
    service = siemplify.extract_action_param("Service", print_value=True)
    threat_name = siemplify.extract_action_param("Filter - Threat Name", print_value=True,
                                                    default_value=None, input_type=str)
    start_date = siemplify.extract_action_param("Filter - Start Date", print_value=True,
                                                    default_value=None, input_type=str)
    end_date = siemplify.extract_action_param("Filter - End Date", print_value=True,
                                                    default_value=None, input_type=str)
    file_path = siemplify.extract_action_param("Filter - File Path", print_value=True,
                                                    default_value=None, input_type=str)
    ip_addr = siemplify.extract_action_param("Filter - IP Address", print_value=True,
                                                    default_value=None, input_type=str)
    action_status = siemplify.extract_action_param("Filter - Action Status", print_value=True)
    
    try:
        siemplify.LOGGER.info("Connecting to Bitdefender GravityZone Control Center.")
        mtm = BitdefenderGravityZoneManager(api_key, verify_ssl)
        siemplify.LOGGER.info("Connected successfully.")
        
        endpoints_data = mtm.quarantine_item_list(access_url, endpoint_id, service, threat_name, start_date, end_date, file_path, ip_addr, action_status)
        
        status = EXECUTION_STATE_COMPLETED
        output_message = "success"
        result_value = "success"
        siemplify.result.add_result_json(endpoints_data)
        siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
        siemplify.end(output_message, result_value, status)
    except Exception as e:
        siemplify.LOGGER.error("An error occurred: {0}".format(e))
        siemplify.LOGGER.exception(e)
    
if __name__ == "__main__":
    main()