from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import errno
import json
import base64
import os
import re


INTEGRATION_NAME = u"FileUtilities"
SCRIPT_NAME = u"Save Base64 to File"
LOCAL_FOLDER = u"downloads"
AGENT_FOLDER = u"/opt/SiemplifyAgent"

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
    
    
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    base64_inputs = list(filter(None, [x.strip() for x in siemplify.parameters.get("Base64 Input").split(',')]))
    filenames = list(filter(None, [x.strip() for x in siemplify.parameters.get("Filename").split(',')]))
    #file_extension = siemplify.parameters.get("File Extension")
    file_extensions_str = siemplify.parameters.get("File Extension", None)
    file_extensions = []
    if file_extensions_str:
        file_extensions = list(filter(None, [x.strip() for x in file_extensions_str.split(',')]))
    folder_path = os.path.join(siemplify.RUN_FOLDER, LOCAL_FOLDER)
    if siemplify.is_remote:
        folder_path = os.path.join(AGENT_FOLDER, LOCAL_FOLDER)
    if len(file_extensions) > 0:
        while len(file_extensions) < len(list(filenames)):
            file_extensions.append(file_extensions[-1])
        
    json_results = {}
    json_results['files'] = []
    file_paths = []
    try:
        os.makedirs(folder_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    if len(file_extensions) > 0:
        for filename, base64_input, file_extension in zip(filenames, base64_inputs, file_extensions):
            file_path = os.path.join(folder_path, get_valid_filename(filename))
            if not file_extension.startswith("."):
                file_path = file_path + "." + file_extension

            try:
                with open(file_path, "wb") as fh:
                    fh.write(base64.b64decode(base64_input))
            except Exception as e:
                siemplify.LOGGER.error("Error: {}".format(e))
                raise
            file_paths.append(file_path)
            filedets = {}
            filedets['file_name'] = filename
            filedets['file_path'] = file_path
            filename, file_extension = os.path.splitext(file_path)
            filedets['extension'] = file_extension
            json_results['files'].append(filedets)
    else:
        for filename, base64_input in zip(filenames, base64_inputs):
            file_path = os.path.join(folder_path, get_valid_filename(filename))
            
            try:
                with open(file_path, "wb") as fh:
                    fh.write(base64.b64decode(base64_input))
            except Exception as e:
                siemplify.LOGGER.error("Error: {}".format(e))
                raise
            file_paths.append(file_path)
            filedets = {}
            
            filedets['file_name'] = filename
            filedets['file_path'] = file_path
            filename, file_extension = os.path.splitext(file_path)
            filedets['extension'] = file_extension
            
            json_results['files'].append(filedets)
    
    
    status = EXECUTION_STATE_COMPLETED
    siemplify.result.add_result_json(json.dumps(json_results))
    output_message = 'Saved the base64 images to: ' + ",".join(file_paths)
    siemplify.end(output_message, True, status)

if __name__ == "__main__":
    main()