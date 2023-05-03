# ==============================================================================
# title           : Extract Zip Files
# description     : This action will extract ZIP files.  It will use the attachment_id
#                 : attribute of a file entities to pull the file from the case wall and extract it.
#                 : The action will create entities out of the extracted files and save them to the case wall.
# author          : robb@siemplify.co
# date            : 2022-02-18
# python_version  : 3.7
# libraries       :
# requirements    :
# product_version :
# ==============================================================================
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import os
import io


from AttachmentsManager import AttachmentsManager

INTEGRATION_NAME = "FileUtilities"
ACTION_NAME = "Extract Zip Files"
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    
    include_data = siemplify.extract_action_param("Include Data In JSON Result",  print_value=True).lower() == "true"
    bruteforce_password = siemplify.extract_action_param("BruteForce Password", print_value=True).lower() == "true"
    create_entities = siemplify.extract_action_param("Create Entities", print_value=True).lower() == "true"
    add_to_case_wall = siemplify.extract_action_param("Add to Case Wall", print_value=True).lower() == "true"
    #zip_password = siemplify.extract_action_param("Zip File Password", print_value=True)
    #zip_password_delimiter = siemplify.extract_action_param("Zip Password List Delimiter", print_value=True)
    
    zip_passwords = list(filter(None, [x.strip() for x in siemplify.extract_action_param("Zip File Password", default_value="")
                    .split(siemplify.extract_action_param("Zip Password List Delimiter", print_value=True))]))
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = "false"  # Set a simple result value, used for playbook if\else and placeholders.
    attach_mgr = AttachmentsManager(siemplify=siemplify)
    
    extracted_files = {}
    for entity in siemplify.target_entities:
        if entity.entity_type == "FILENAME":
            siemplify.LOGGER.info(f"The entity {entity.identifier} is being checked for being zip")
            if 'attachment_id' in entity.additional_properties and os.path.splitext(entity.identifier)[1].lower() == ".zip":
                _attachment = siemplify.get_attachment(entity.additional_properties['attachment_id'])
                zip_file_content = io.BytesIO(_attachment.getvalue())
                extracted_files[entity.identifier] = attach_mgr.extract_zip(entity.identifier,zip_file_content, bruteforce = bruteforce_password, pwds=zip_passwords)
                result_value = "true"
                        
    if add_to_case_wall:
        for file_name in extracted_files:
            for x_file in extracted_files[file_name]:
                siemplify.LOGGER.info(f"Adding the file: {x_file['filename']} to the case wall")
                attachment_res = attach_mgr.add_attachment(x_file['filename'], x_file['raw'], siemplify.case_id, siemplify.alert_id)
                x_file['attachment_id'] = attachment_res

    if include_data == False:
        for file_name in extracted_files:
            x_files = extracted_files[file_name]
            for x_file in extracted_files[file_name]:
                del x_file['raw']
            
    if create_entities:
        for file_name in extracted_files:
            siemplify.result.add_json(file_name, extracted_files[file_name],"Zip File")
            attach_mgr.create_file_entities(extracted_files[file_name])
    
    siemplify.result.add_result_json(convert_dict_to_json_result_dict(extracted_files))
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
