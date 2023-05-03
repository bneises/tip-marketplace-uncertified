from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json
import time
from datetime import datetime

TASK_URL = '{}/external/v1/cases/AssignUserToCase'
ACTION_NAME = "AssignCaseToUser"

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    

    case_id = siemplify.parameters['Case Id']
    assign_to = siemplify.parameters['Assign To']
    alert_id = siemplify.parameters['Alert Id']

    

    json_payload = {"caseId": case_id, "alertIdentifier": alert_id, "userId": assign_to}
    add_task = siemplify.session.post(TASK_URL.format(siemplify.API_ROOT), json=json_payload)
    add_task.raise_for_status()
    output_message = add_task.json()
    siemplify.LOGGER.info(output_message)
    
    siemplify.end(output_message, True)

if __name__ == "__main__":
    main()