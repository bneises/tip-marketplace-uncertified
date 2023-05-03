from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json

DESC_URL = '{}/external/v1/cases/ChangeCaseDescription'
ACTION_NAME = "UpdateCaseDescription"

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    description = siemplify.parameters['Case Description']
    case_id = siemplify.case_id
    json_payload = {"caseId": case_id, "description": description}
    update_description = siemplify.session.post(DESC_URL.format(siemplify.API_ROOT), json=json_payload)
    update_description.raise_for_status()
   
    output_message = "The case description has been updated to: {}".format(description)
    siemplify.end(output_message, True)

if __name__ == "__main__":
    main()