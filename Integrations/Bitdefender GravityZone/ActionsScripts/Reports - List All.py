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
    report_name = siemplify.extract_action_param("Report Name", print_value=True,
                                                    default_value=None, input_type=str)
    report_type = siemplify.extract_action_param("Report Type", print_value=True,
                                                    default_value=None, input_type=str)
    
    try:
        siemplify.LOGGER.info("Connecting to Bitdefender GravityZone Control Center.")
        mtm = BitdefenderGravityZoneManager(api_key, verify_ssl)
        siemplify.LOGGER.info("Connected successfully.")
        
        policies_data = mtm.report_list(access_url, report_name, report_type)
        
        status = EXECUTION_STATE_COMPLETED
        output_message = "success"
        result_value = "success"
        siemplify.result.add_result_json(policies_data)
        siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
        siemplify.end(output_message, result_value, status)
    except Exception as e:
        siemplify.LOGGER.error("An error occurred: {0}".format(e))
        siemplify.LOGGER.exception(e)
    
if __name__ == "__main__":
    main()