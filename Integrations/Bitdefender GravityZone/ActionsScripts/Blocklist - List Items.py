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
    use_json_filter = siemplify.extract_action_param("Use JSON Filter", print_value=True)
    query_filter = siemplify.extract_action_param("Filter", print_value=True)
    parent_id = siemplify.extract_action_param("Parent ID", print_value=True)
    endpoints = siemplify.extract_action_param("Endpoints", print_value=True)
    
    try:
        siemplify.LOGGER.info("Connecting to Bitdefender GravityZone Control Center.")
        mtm = BitdefenderGravityZoneManager(api_key, verify_ssl)
        siemplify.LOGGER.info("Connected successfully.")
        
        endpoints_data = mtm.blocklist_hashes_list(access_url)
        
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