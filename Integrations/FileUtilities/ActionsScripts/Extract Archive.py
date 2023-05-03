# ==============================================================================
# title           : Extract Archive
# description     : This action will extract an archive to a directory.  Returns list
#                 : of all files extracted
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
import json


DEST_DIR = '/opt/siemplify/siemplify_server/Scripting/FileUtilities/Extract'

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    filename, file_extension = os.path.splitext(path)
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
        d['extension'] = file_extension
        d['path'] = path
    return d

@output_handler
def main():
    siemplify = SiemplifyAction()
    archives = list(filter(None, [x.strip() for x in siemplify.parameters.get("Archive").split(',')]))
    
    status              = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message      = "output message :"  # human readable message, showed in UI as the action result
    result_value        = None  # Set a simple result value, used for playbook if\else and placeholders.
    json_result = {}
    success_files = []
    failed_files = []
    json_result['archives'] = []
    for archive in archives:
        archive_name = pathlib.Path(archive).stem
        full_archive_name = pathlib.Path(archive).name
    
        output_dir = os.path.join(DEST_DIR, archive_name)
        if not os.path.exists(output_dir):
            try: 
                pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
            except OSError:
                siemplify.LOGGER.error("Creation of the directory %s failed" % output_dir)
                status      = EXECUTION_STATE_FAILED
                json_result['archives'].append({"success": False, "archive": full_archive_name })
                failed_files.append(archive)
                raise
        try:    
            files = shutil.unpack_archive(archive, output_dir)
            files = path_to_dict(output_dir)
            files_w_path = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            onlyfiles = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            json_result['archives'].append({"success": True, "archive": full_archive_name, "folder": output_dir, "files": files, "files_with_path": files_w_path, "files_list": onlyfiles} )
            output_message = "\nSuccessfully extracted archive: {}".format(full_archive_name)
            success_files.append(archive)
        except Exception as e:
            siemplify.LOGGER.error("General error performing action:\r")
            siemplify.LOGGER.exception(e)
            status          = EXECUTION_STATE_FAILED
            result_value    = "Failed"
            output_message += "\n" + e
            json_result['archives'].append({"success": False, "archive": full_archive_name  })
            failed_files.append(archive)
            raise
    if not failed_files:
        result_value = True
    siemplify.result.add_result_json(json_result)      
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()