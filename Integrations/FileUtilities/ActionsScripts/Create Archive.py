# ==============================================================================
# title           : Create Archive
# description     : This action will create an archive from a list of supplied files or directories.
# author          : robb@siemplify.co
# date            : 2021-01-08
# python_version  : 3.7
# libraries       : shutil, os, tempfile, pathlib
# requirements    :
# product_version :
# ==============================================================================
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT


import shutil
import os
import tempfile
import pathlib

DEST_DIR = '/opt/siemplify/siemplify_server/Scripting/FileUtilities/Archives'

def copy_files_to_temp_dir(archive_input):
    tmp_dir = tempfile.mkdtemp()
    for file in archive_input:
        shutil.copy2(file, tmp_dir)
    return tmp_dir

    
@output_handler
def main():
    siemplify = SiemplifyAction()
    
    archive_type =  siemplify.extract_action_param("Archive Type", print_value=True)
    archive_input = list(filter(None, [x.strip() for x in siemplify.extract_action_param("Archive Input",print_value=True).split(',')]))
    archive_name       = siemplify.extract_action_param("Archive Base Name", print_value=True)
    
    
    status              = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message      = "output message :"  # human readable message, showed in UI as the action result
    result_value        = None  # Set a simple result value, used for playbook if\else and placeholders.

    #Does directory exist? If not, then create it.
    
    if not os.path.exists(DEST_DIR):
        try: 
            pathlib.Path(DEST_DIR).mkdir(parents=True, exist_ok=True)
        except OSError:
            siemplify.LOGGER.error("Creation of the directory %s failed" % DEST_DIR)
            status      = EXECUTION_STATE_FAILED
    
    try:
        archive_path = os.path.join(DEST_DIR, archive_name)
        
        if os.path.isdir(archive_input[0]):
            archive_output =  shutil.make_archive(archive_path, archive_type, archive_input[0])
            
        elif os.path.isfile(archive_input[0]):
            tmp_dir = copy_files_to_temp_dir(archive_input)
            archive_output = shutil.make_archive(archive_path, archive_type, tmp_dir)
            shutil.rmtree(tmp_dir)
            
            
        else:
            siemplify.LOGGER.error("Archive input is not file or directory.")
            raise Exception('Unknown Input Type', "Archive input is not file or directory")
        
        json_result =  {"success": True, "archive": archive_output} 
        result_value = archive_output
        siemplify.result.add_result_json(json_result)
        output_message = "Successfully created archive: {}".format(archive_output)
    except Exception as e:
        siemplify.LOGGER.error("General error performing action:\r")
        siemplify.LOGGER.exception(e)
        status          = EXECUTION_STATE_FAILED
        result_value    = "Failed"
        output_message += "\n" + e
        raise
       

    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()