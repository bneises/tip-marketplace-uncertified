# ==============================================================================
# title          :Detect Hash Type.py
# description    :This action detects the most likely hash type of entities. Supported types are SHA256, MD5, SHA1, SHA-512.
# author         :elisv@siemplify.co
# date           :19-05-2021
# python_version :3.7
# ==============================================================================

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from hashid import *

SUPPORTED_OUTPUT_TYPES = {"SHA-256", "MD5", "SHA-1", "SHA-512"}


@output_handler
def main():
    siemplify = SiemplifyAction()

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "Most likely hash types found"  # human readable message, showed in UI as the action result
    result_value = "true"  # Set a simple result value, used for playbook if\else and placeholders.

    res = []
    to_enrich = []
    hid = HashID()
    
    hashes = siemplify.parameters.get("Hashes")
    if hashes:
        hashes = hashes.split(",")
    try:
        for _hash in hashes:
            intersection = list(set([x.name for x in hid.identifyHash(_hash)]).intersection(SUPPORTED_OUTPUT_TYPES))
            if intersection:
                res.append({"Hash": _hash, "HashType": intersection[0]})
            else:
                res.append({"Hash": _hash, "HashType": "UNDETECTED"})
    
        for entity in siemplify.target_entities:
            if entity.entity_type == "FILEHASH":
                intersection = list(set([x.name for x in hid.identifyHash(entity.identifier)]).intersection(SUPPORTED_OUTPUT_TYPES))
                if intersection:
                    d = {"HashType": intersection[0]}
                else:
                    d = {"HashType": "UNDETECTED"}
                entity.additional_properties.update(d)
                to_enrich.append(entity)
                d["Hash"] = entity.identifier
                res.append(d)
    
        if to_enrich:
            siemplify.update_entities(to_enrich)
        
        siemplify.result.add_result_json(res)
        siemplify.result.add_json("Hash Types", res)
    except Exception as e:
        status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        result_value = False

    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)



if __name__ == "__main__":
    main()
