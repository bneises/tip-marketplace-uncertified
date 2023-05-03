from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from WorkflowToolsManager import WorkflowToolsManager


MSG_APPROVED = ":large_green_circle: Case <{0}/#/main/cases/classic-view/{1}|{1}> has been *approved* by {2}."

MSG_DENIED = ":red_circle: Case <{0}/#/main/cases/classic-view/{1}|{1}> has been *denied* for workflow approval by {2}."

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    output_message = "Action Denied"  # human readable message, showed in UI as the action result
    result_value = False  # Set a simple result value, used for playbook if\else and placeholders.
    json_result = {"reason":"", "reviewer":"", "review_comments":"", "approved":False}

    api_key = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Key")
    api_root = siemplify.extract_configuration_param('Workflow Tools',"Siemplify API Root")
    siemplify_hostname = siemplify.extract_configuration_param('Workflow Tools',"Siemplify Instance Hostname")
    slack_webhook_url = siemplify.extract_configuration_param('Workflow Tools',"Slack Webhook URL")
    # The user that is permitted to continue this action
    reviewer = siemplify.extract_configuration_param('Workflow Tools', "Approval Manager")
    reviewer_secondary = siemplify.extract_configuration_param('Workflow Tools', "Secondary Approval Manager",
                                             default_value="", input_type=str)
    response_comments = siemplify.extract_action_param("Response Comments", print_value=True,
                                             default_value="", input_type=str)
    approval_result = siemplify.extract_action_param("Action Approved", print_value=True, input_type=bool)
    
    manager = WorkflowToolsManager(siemplify_hostname=siemplify_hostname, api_root=api_root, api_key=api_key, siemplify=siemplify, slack_webhook_url=slack_webhook_url)
    
    # The ID of the case
    case_id = siemplify.case.identifier
    # The ID of the current alert
    alert_id = siemplify.current_alert.identifier
    # The user that's requesting to interact with this action
    requesting_user = siemplify.original_requesting_user
    
    siemplify.LOGGER.info("Beginning Processing of Case {}".format(case_id))
    siemplify.LOGGER.info("Alert ID {}".format(alert_id))
    
    siemplify.LOGGER.info("Original Requesting User {}".format(siemplify.original_requesting_user))
    
    ### STEP 1: Check if the current user is allowed to continue this action.
    
    if(manager.check_user(current_user=requesting_user, approval_manager=reviewer) or
        manager.check_user(current_user=requesting_user, approval_manager=reviewer_secondary)):
        siemplify.LOGGER.info("Case {} is assigned to required reviewer {}. Continuing action.".format(case_id, reviewer))
        response_message = ""
        
        if(approval_result):
            response_message = MSG_APPROVED.format(manager.siemplify_hostname,case_id, requesting_user)
            json_result['approved'] = True
            output_message = "Action Approved"
            result_value = True
            result_value = True
        else:
            response_message = MSG_DENIED.format(manager.siemplify_hostname, case_id, requesting_user)
            json_result['reason'] = "Case {0} has been denied workflow approval by {1}".format(case_id, requesting_user)
        
        if(response_comments):
            response_message = "{0}\n>*Comments:*\n>{1}".format(response_message, response_comments)
            siemplify.add_comment(response_comments, case_id=case_id, alert_identifier=alert_id)
            json_result['review_comments'] = response_comments
            
        manager.log_slack_message(response_message)
        json_result['reviewer'] = requesting_user
        
    else:
        ## DISALLOW any further activity
        siemplify.LOGGER.info("Case {} is NOT assigned to required reviewer {}. Cancelling.".format(case_id, reviewer))
        e = "Failed to approve action in case <{0}/#/main/cases/classic-view/{1}|{1}>. User {2} is unauthorized.".format(manager.siemplify_hostname, case_id, requesting_user)
        manager.log_slack_message(message=e)
        siemplify.LOGGER.error(e)
        siemplify.LOGGER.exception(e)
        raise ValueError(e)
        
        
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    siemplify.result.add_result_json(json_result)
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {} \nOriginal Requesting User: {}".format(status,result_value, output_message, siemplify.original_requesting_user))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
