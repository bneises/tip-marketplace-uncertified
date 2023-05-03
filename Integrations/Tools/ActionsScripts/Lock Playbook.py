from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_INPROGRESS
GET_CASE_FULL_DETAILS = '{}/external/v1/cases/GetCaseFullDetails/{}'
WF_STATUS_INPROGRESS = 1
WF_STATUS_COMPLETED = 2
WF_STATUS_FAILED = 3
WF_STATUS_PENDING = 4
WF_STATUS_TERMINATED = 5



@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "Lock Playbook"
    res = siemplify.session.get(GET_CASE_FULL_DETAILS.format(siemplify.API_ROOT, siemplify.case_id))
    siemplify.validate_siemplify_error(res)
    case = res.json()
    current_alert_index = None
    alerts = list(reversed(case["alerts"]))
    if siemplify.current_alert.identifier == siemplify.case.alerts[-1].identifier:
        output_message = f"Alert Index: {current_alert_index}. Alert Id: {siemplify.current_alert.identifier}: First alert - continuing playbook."
        result_value = 'true'
        status = EXECUTION_STATE_COMPLETED
    else:
        for alert_index, alert in enumerate(alerts):
            if alert["identifier"] == siemplify.alert_id:
                current_alert_index = alert_index
                siemplify.LOGGER.info("alert id: {} alert index: {}".format(siemplify.alert_id, current_alert_index))
                break
        if current_alert_index != None:
            if siemplify.current_alert.identifier == siemplify.case.alerts[-1].identifier:
                output_message = f"Alert Index: {current_alert_index}. Alert Id: {siemplify.current_alert.identifier}: First alert - continuing playbook."
                result_value = 'true'
                status = EXECUTION_STATE_COMPLETED
            elif alerts[current_alert_index - 1]["workflowsStatus"] == WF_STATUS_INPROGRESS:
                prev_case= alerts[current_alert_index - 1]["identifier"]
                output_message = f"Alert Index: {current_alert_index}. Alert Id: {siemplify.current_alert.identifier}: Playbook Locked. Waiting for alert # {prev_case} playbook to finish."
                result_value = 'false'
                status = EXECUTION_STATE_INPROGRESS
            else:
                output_message = f"Alert Index: {current_alert_index}. Alert Id: {siemplify.current_alert.identifier}: Lock Released. "
                result_value = 'true'
                status = EXECUTION_STATE_COMPLETED
        else:
            status = EXECUTION_STATE_FAILED
            output_message = "Couldn't find current alert"
            result_value = 'false'
    siemplify.end(output_message, result_value, status)
if __name__ == "__main__":
    main()