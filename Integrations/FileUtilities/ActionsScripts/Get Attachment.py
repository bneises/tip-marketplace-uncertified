from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

import json
import requests
import base64

def main():
    siemplify = SiemplifyAction()
    scope = siemplify.parameters.get("Attachment Scope")
    headers = {'AppKey': siemplify.api_key}
    response = requests.get(f'{siemplify.API_ROOT}/external/v1/cases/GetCaseFullDetails/' + siemplify.case.identifier,headers=headers, verify=False)
    wall_items = response.json()['wallData']
    attachments = []
    for wall_item in wall_items:
        if wall_item['type'] == 4:
            if(scope.lower() == 'alert'):
                if siemplify.current_alert.identifier == wall_item['alertIdentifier']:
                    attachments.append(wall_item)
            else:
                attachments.append(wall_item)

    for attachment in attachments:
        attachment_record = siemplify.get_attachment(attachment['id'])
        attachment_content = attachment_record.getvalue()
        b64 = base64.b64encode(attachment_content)
        attachment['base64_blob'] = b64.decode('ascii')

    siemplify.result.add_result_json(json.dumps(attachments))


    siemplify.end('{} attachment(s) found'.format(len(attachments)), len(attachments))




if __name__ == "__main__":
    main()
