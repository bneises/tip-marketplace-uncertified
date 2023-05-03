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
    parent_id = siemplify.extract_action_param("Parent ID", print_value=True,
                                                    default_value=None, input_type=str)
    endpoints = siemplify.extract_action_param("Endpoints", print_value=True)
    filter_best = siemplify.extract_action_param("Filter - Managed with BEST", print_value=True,
                                                    default_value=False, input_type=bool)
    filter_exchange = siemplify.extract_action_param("Filter - Managed Exchange Servers", print_value=True,
                                                    default_value=False, input_type=bool)
    filter_relays = siemplify.extract_action_param("Filter - Managed Relays", print_value=True,
                                                    default_value=False, input_type=bool)
    filter_security_servers = siemplify.extract_action_param("Filter - Security Servers", print_value=True,
                                                    default_value=False, input_type=bool)
    filter_depth_allrecursive = siemplify.extract_action_param("Filter - Depth - All Items Recursively", print_value=True,
                                                    default_value=False, input_type=bool)
    filter_ssid = siemplify.extract_action_param("Filter - SSID", print_value=True,
                                                    default_value=None, input_type=str)
    filter_macaddrs = siemplify.extract_action_param("Filter - MAC Addresses", print_value=True,
                                                    default_value=None, input_type=str)
    filter_name = siemplify.extract_action_param("Filter - Name", print_value=True,
                                                    default_value=None, input_type=str)
    
    try:
        siemplify.LOGGER.info("Connecting to Bitdefender GravityZone Control Center.")
        mtm = BitdefenderGravityZoneManager(api_key, verify_ssl)
        siemplify.LOGGER.info("Connected successfully.")
        
        endpoints_data = mtm.get_endpoints_list(access_url, parent_id, endpoints, filter_best, filter_exchange, 
        filter_relays, filter_security_servers, filter_depth_allrecursive, filter_ssid, filter_macaddrs, filter_name)
        
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