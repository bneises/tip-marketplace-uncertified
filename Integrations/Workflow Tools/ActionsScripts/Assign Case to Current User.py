from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from WorkflowToolsManager import WorkflowToolsManager


@output_handler
def main():
    SYSTEM_USER = "System"
    siemplify = SiemplifyAction()

    # A Siemplify API key is required to interact with the API
    api_key = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Key")
    api_root = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Root")
    siemplify_hostname = siemplify.extract_configuration_param('Workflow Tools',"Siemplify Instance Hostname")
    
    manager = WorkflowToolsManager(siemplify_hostname=siemplify_hostname, api_root=api_root, api_key=api_key, siemplify=siemplify)
    # The ID of the case
    case_id = siemplify.case.identifier
    # The ID of the current alert
    alert_id = siemplify.current_alert.identifier
    # The user that executed this action
    requesting_user = siemplify.original_requesting_user
    if(requesting_user!=SYSTEM_USER):
        siemplify.LOGGER.info("Attempting to assign case {} to user: {}".format(case_id, requesting_user))
        manager.assign_case(requesting_user, case_id, alert_id)
    else:
        e = "\"Assign Case to Current User\" action failed on case {} because the user was \"{}\": This playbook action must be set to manual excecution to work.".format(case_id, requesting_user)
        siemplify.LOGGER.error(e)
        siemplify.LOGGER.exception(e)
        raise ValueError(e)
    
    status = EXECUTION_STATE_COMPLETED
    output_message = "output message : Assigned case to {}".format(requesting_user)
    result_value = requesting_user
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
