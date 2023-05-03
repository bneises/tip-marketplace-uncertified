from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_INPROGRESS
GET_CASE_FULL_DETAILS = '{}/external/v1/cases/GetCaseFullDetails/{}'
GET_ALERT_WFS = '{}/external/v1/cases/GetWorkflowInstancesCards?format=camel'


WF_STATUS_INPROGRESS = 1
WF_STATUS_COMPLETED = 2
WF_STATUS_FAILED = 3
WF_STATUS_PENDING = 4
WF_STATUS_TERMINATED = 5


def get_wf_status(siemplify, workflow_name):
    res = siemplify.session.get(GET_CASE_FULL_DETAILS.format(siemplify.API_ROOT, siemplify.case_id))
    siemplify.validate_siemplify_error(res)
    case = res.json()
    current_alert_index = None
    alerts = sorted(case["alerts"], key=lambda x: x["creationTimeUnixTimeInMs"], reverse=True)
    alert_id = None
    for alert in alerts:
        if alert["identifier"] == siemplify.alert_id:
            alert_id = alert['additionalProperties']['alertGroupIdentifier']
            current_alert_index = case["alerts"].index(alert)
    payload = {}
    payload['caseId'] = siemplify.case_id
    payload['alertIdentifier'] = alert_id
    alert_wfs_res = siemplify.session.post(GET_ALERT_WFS.format(siemplify.API_ROOT), json=payload)
    siemplify.validate_siemplify_error(alert_wfs_res)
    for alert_wf in alert_wfs_res.json():
        if alert_wf['name'] == workflow_name:
            return alert_wf['status']
            
    
 
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "Wait for Playbook to Complete"
    playbook_name = siemplify.parameters.get("Playbook Name", None)
    wf_status = get_wf_status(siemplify, playbook_name)
    
    
    if wf_status == WF_STATUS_COMPLETED:
        output_message = f"Alert Id: {siemplify.current_alert.identifier}, Playbook: {playbook_name} Finished. Lock Released. "
        result_value = 'true'
        status = EXECUTION_STATE_COMPLETED
    elif wf_status == WF_STATUS_FAILED:
        output_message = f"Alert Id: {siemplify.current_alert.identifier}, Playbook: {playbook_name} Failed. Lock Released. "
        result_value = 'true'
        status = EXECUTION_STATE_COMPLETED
    elif wf_status == WF_STATUS_TERMINATED:
        output_message = f"Alert Id: {siemplify.current_alert.identifier}, Playbook: {playbook_name} terminated. Lock Released. "
        result_value = 'true'
        status = EXECUTION_STATE_COMPLETED
    elif wf_status == WF_STATUS_INPROGRESS or wf_status == WF_STATUS_PENDING:
        
        output_message = f"Alert Id: {siemplify.current_alert.identifier}: Playbook {playbook_name} Inprogress. Current playbook locked."
        result_value = 'false'
        status = EXECUTION_STATE_INPROGRESS
    else:
        output_message = f"Alert Id: {siemplify.current_alert.identifier}: Playbook {playbook_name} not found."
        result_value = 'true'
        status =         status = EXECUTION_STATE_COMPLETED


    siemplify.end(output_message, result_value, status)
if __name__ == "__main__":
    main()