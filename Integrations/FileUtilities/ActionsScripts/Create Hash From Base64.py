# ==============================================================================
# title          :Create Hash From File.py
# description    :Returns hashes for provided base64s
# author         :elisv@siemplify.co
# date           :19-03-2021
# python_version :3.7
# ==============================================================================

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import hashlib
import base64


SCRIPT_NAME = "Create Hash From Base64"
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    
    action_status = EXECUTION_STATE_COMPLETED
    action_result = True
    output_message = "Successfully created hash from base64."
    res = []
    strings = siemplify.parameters["Base64"].split(siemplify.parameters["Base64 Separator"])
    hash_algorythm = siemplify.parameters["Hash Algorythm"]
    names = siemplify.parameters.get("Names")
    try:
        if names:
            names = names.split(siemplify.parameters["Names Separator"])
    
            for s, n in zip(strings, names):
                d = {"Hash": getattr(hashlib, hash_algorythm)(base64.b64decode(s)).hexdigest(), "HashAlgorythm": hash_algorythm}
                if siemplify.parameters["Include Base64"].lower() == "true":
                    d["Base64"] = s
                d["Name"] = n
                res.append(d)
        else:
            for s in strings:
                d = {"Hash": getattr(hashlib, hash_algorythm)(base64.b64decode(s)).hexdigest(), "HashAlgorythm": hash_algorythm}
                if siemplify.parameters["Include Base64"].lower() == "true":
                    d["Base64"] = s
                res.append(d)
        siemplify.result.add_json("Hashes", res)
        siemplify.result.add_result_json(res)
    except Exception as e:
        action_status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        action_result = False


    siemplify.end(output_message, action_result, action_status)


if __name__ == "__main__":
    main()
