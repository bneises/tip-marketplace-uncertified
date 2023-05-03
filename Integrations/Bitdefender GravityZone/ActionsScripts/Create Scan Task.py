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
    target_ids = siemplify.extract_action_param("Target IDs", print_value=True)
    scan_type = siemplify.extract_action_param("Scan Type", print_value=True)
    task_name = siemplify.extract_action_param("Task Name", print_value=True)
    scan_depth = siemplify.extract_action_param("Custom Scan - Depth", print_value=True)
    scan_paths = siemplify.extract_action_param("Custom Scan - Paths", print_value=True)
    
    try:
        siemplify.LOGGER.info("Connecting to Bitdefender GravityZone Control Center.")
        mtm = BitdefenderGravityZoneManager(api_key, verify_ssl)
        siemplify.LOGGER.info("Connected successfully.")
        
        result = mtm.task_create_scan(access_url, target_ids, scan_type, task_name, scan_depth, scan_paths)
        
        status = EXECUTION_STATE_COMPLETED
        output_message = "success"
        result_value = "success"
        if not result:
            result_value = "failed"
            output_message = "failed"
        siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
        siemplify.end(output_message, result_value, status)
    except Exception as e:
        siemplify.LOGGER.error("An error occurred: {0}".format(e))
        siemplify.LOGGER.exception(e)
    
if __name__ == "__main__":
    main()