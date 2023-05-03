from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import Attachment
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, add_prefix_to_dict, dict_to_flat, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import datetime
import json
import base64

from EmailManager import EmailManager, EmailUtils
from AttachmentsManager import AttachmentsManager



import os
import time
import copy

SUPPORTED_ATTACHMENTS = [".eml", ".msg"]
ORIG_EMAIL_DESCRIPTION = ["This is the original message as EML", "Original email attachment"]

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    elif isinstance(obj, bytes):

        return base64.b64encode(obj).decode()
    raise TypeError("Type not serializable")
    
        
@output_handler
def main():
    siemplify = SiemplifyAction()
    
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = ""  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    siemplify.script_name = "Parse Email"
    siemplify.LOGGER.info(f"Starting {siemplify.script_name}.")
    
    save_to_case_wall = siemplify.parameters["Save Attachments to Case Wall"].lower() == "true"
    create_base_entities = siemplify.parameters["Create Entities"].lower() == "true"
    create_observed_entity_types = siemplify.parameters.get("Create Observed Entities", "All")
    original_eml_only = siemplify.parameters["Original EML Only"].lower() == "true"

    exclude_regex = siemplify.parameters.get("Exclude Entities Regex", None)
    fang_entities = siemplify.parameters["Fang Entities"].lower() == "true"
    custom_regex = siemplify.parameters.get("Custom Entity Regexes", "{}")
    
    try:
        custom_regex = json.loads(custom_regex)
    except:
        output_message += "\nFailed to load custom regex mappings."
        custom_regex = {}

    parsed_emails = []

    
    
    email_mgr = EmailManager(siemplify=siemplify, logger=siemplify.LOGGER, custom_regex=custom_regex)
    attach_mgr = AttachmentsManager(siemplify=siemplify)
    attachments = attach_mgr.get_alert_attachments()# 
    
    orig_email_attachment = {}
    attached_email = {}
    
    for eml_attachment in attachments:
        if eml_attachment['description'] in ORIG_EMAIL_DESCRIPTION and eml_attachment['fileType'] in SUPPORTED_ATTACHMENTS:
            orig_email_attachment = eml_attachment
        elif eml_attachment['fileType'] in SUPPORTED_ATTACHMENTS and not eml_attachment['description'] in ORIG_EMAIL_DESCRIPTION:
            attached_email = eml_attachment
            
    if attached_email and not original_eml_only:
        attachment = attached_email
    else:
        attachment = orig_email_attachment
    
    if not attachment:
        attachments = attach_mgr.get_attachments()
        orig_email_attachment = {}
        attached_email = {}
    
        for eml_attachment in attachments:
            if eml_attachment['description'] in ORIG_EMAIL_DESCRIPTION and eml_attachment['fileType'] in SUPPORTED_ATTACHMENTS:
                orig_email_attachment = eml_attachment
            elif eml_attachment['fileType'] in SUPPORTED_ATTACHMENTS and not eml_attachment['description'] in ORIG_EMAIL_DESCRIPTION:
                attached_email = eml_attachment
            
        if attached_email:
            attachment = attached_email
        else:
            attachment = orig_email_attachment

    attachment_record = siemplify.get_attachment(attachment['id'])
    attachment_name = f"{attachment['evidenceName']}{attachment['fileType']}"
    attachment_content = attachment_record.getvalue()
    siemplify.LOGGER.info(f"Extracting from Case Wall Attachment: {attachment_name}")
    parsed_email = email_mgr.parse_email(attachment_name, attachment_content)
    parsed_email['attachment_name'] = f"{attachment['evidenceName']}{attachment['fileType']}"
    parsed_email['attachment_id'] = attachment['id']
    parsed_emails.append(parsed_email)
            
    if create_observed_entity_types != "None" or create_base_entities:
        sorted_emails = sorted(parsed_email['attached_emails'], key=lambda d: d['level'], reverse=True) 
        for r_email in sorted_emails:
            email_mgr.create_entities(create_base_entities, create_observed_entity_types, exclude_regex, r_email, fang_entities)
                    
    if save_to_case_wall:
        updated_entities = []
        for attachment in parsed_email['attachments']:
            if attachment['raw']  != '':
                try:
                    attachment_res = attach_mgr.add_attachment(attachment['filename'], attachment['raw'], siemplify.case_id, siemplify.alert_id)
                    del attachment['raw']
                    name, attachment_type = os.path.splitext(attachment['filename'].strip().upper())
                    for entity in email_mgr.get_alert_entities():
                        if (attachment['filename'].strip().upper() == entity.identifier.strip().upper() or name == entity.identifier.strip().upper())  and entity.entity_type == "FILENAME":
                            entity.additional_properties['attachment_id'] = attachment_res
                            updated_entities.append(entity)
                            break
                except Exception as e: 
                    if 'raw' in attachment:
                        del attachment['raw']
                    siemplify.LOGGER.error(e)
                    output_message += f"Unable to add file {attachment['filename']}.  "
                    raise

        if updated_entities:
            siemplify.LOGGER.info(f"updating file entity attachment_id: {updated_entities}")
            siemplify.update_entities(updated_entities)     
    siemplify.result.add_json(attachment_name, parsed_email,"Email File")
                
            
    
    #print(json.dumps({"parsed_emails": parsed_emails}, sort_keys=True, default=json_serial))
    siemplify.result.add_result_json(json.dumps({"parsed_emails": parsed_emails}, sort_keys=True, default=json_serial))

    output_message += "Parsed message file."
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()