from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from WorkflowToolsManager import WorkflowToolsManager
import requests
import json 

MSG_AWAITING_APPROVAL = ":large_orange_circle: Case <{0}/#/main/cases/classic-view/{1}|{1}> is awaiting workflow approval."

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    output_message = "output message: "  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    
    # A Siemplify API key is required to interact with the API
    api_key = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Key")
    api_root = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Root")
    siemplify_hostname = siemplify.extract_configuration_param('Workflow Tools',"Siemplify Instance Hostname")
    slack_webhook_url = siemplify.extract_configuration_param('Workflow Tools',"Slack Webhook URL")
    # The approval manager that the case/alert should be assigned to
    reviewer = siemplify.extract_configuration_param('Workflow Tools', "Approval Manager")
    reviewer_secondary = siemplify.extract_configuration_param('Workflow Tools', "Secondary Approval Manager",
                                             default_value="", input_type=str)
    move_grouped_alert = siemplify.extract_action_param("Move Alert If Grouped", print_value=True, input_type=bool)
    # JSON Result object returned at execution end.
    json_result = {"approval_manager": reviewer, "secondary_approval_manager": reviewer_secondary, 
                        "original_case_id": -1, "new_case_id": -1}
    
    
    manager = WorkflowToolsManager(siemplify_hostname=siemplify_hostname, api_root=api_root, api_key=api_key, siemplify=siemplify, slack_webhook_url=slack_webhook_url)
    
    # The ID of the case
    case_id = siemplify.case.identifier
    json_result['original_case_id'] = case_id
    # The ID of the current alert
    alert_id = siemplify.current_alert.identifier
    
    result_value = True
    ### STEP 1: Check whether to move the alert to a new case, if grouped with others
    if(move_grouped_alert == False):
        ### STEP 2a: The case is to be treated as one workflow, don't worry about moving the alert. Treat the case as a whole. 
        manager.assign_case(reviewer, case_id, alert_id)
        manager.log_slack_message(message=MSG_AWAITING_APPROVAL.format(manager.siemplify_hostname,case_id))
        output_message = output_message + "Case was assigned to reviewer for approval."
    else:
        ### STEP 2b: If we're to move the alert when grouped with others, check if there's more than one alert.
        if(int(siemplify.case.alert_count) > 1):
            ### STEP 2b i:
            ### Move the alert to its own case.
            new_case_id = manager.move_alert(case_id, alert_id)
            if(new_case_id == None):
                e = "Failed to move alert {} from case {}. Did not receive a new case ID from API.".format(alert_id, case_id)
                siemplify.LOGGER.error(e)
                siemplify.LOGGER.exception(e)
                raise ValueError(e)
            json_result['new_case_id'] = new_case_id
            ### Assign the new case to approval manager, send slack message
            output_message = output_message + "Alert {0} was moved to new case {1} for approval.".format(alert_id, new_case_id)
            manager.assign_case(reviewer, new_case_id, alert_id)
            manager.log_slack_message(message=MSG_AWAITING_APPROVAL.format(manager.siemplify_hostname,new_case_id))
        else:
            ### STEP 2b ii:
            ### Assign the case to the approval manager, send slack message
            manager.assign_case(reviewer, case_id, alert_id)
            output_message = output_message + "Case was assigned to reviewer for approval."
            manager.log_slack_message(message=MSG_AWAITING_APPROVAL.format(manager.siemplify_hostname,case_id))
    
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    siemplify.result.add_result_json(json_result)
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {} \nAssigned to Approval Manager: {}".format(status,result_value, output_message, reviewer))
    siemplify.end(output_message, result_value, status)

if __name__ == "__main__":
    main()
