from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

import json
import requests
import base64


    
def main():
    siemplify = SiemplifyAction()
    
    description = siemplify.parameters.get("Description")
    name = siemplify.parameters.get("Name")
    file_type = siemplify.parameters.get("Type")
    base64_blob = siemplify.parameters.get("Base64 Blob")
    isFavorite = bool(siemplify.parameters.get("isFavorite"))
    headers = {'AppKey': siemplify.api_key,"Content-Type":"application/json"}
    case_id = int(siemplify.case.identifier)
    
    body = {
        "CaseIdentifier": case_id,
        "Base64Blob": base64_blob,
        "Name": name,
        "Description": description,
        "Type":file_type,
        "IsImportant": isFavorite
    }
    response = requests.post(f'{siemplify.API_ROOT}/external/v1/cases/AddEvidence/',headers=headers, data = json.dumps(body), verify=False)
    json_response = response.json()

    
    siemplify.result.add_result_json(json.dumps(json_response))


    siemplify.end('Max number , Min Number', True)




if __name__ == "__main__":
    main()
