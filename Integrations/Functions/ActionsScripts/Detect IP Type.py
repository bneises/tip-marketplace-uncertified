# ==============================================================================
# title          :Detect IP Type.py
# description    :This action detects the IP type of entities.
# author         :elisv@siemplify.co
# date           :15-06-2021
# python_version :3.7
# ==============================================================================

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import re

IPV4 = "^(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))$"
IPV6 = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"


@output_handler
def main():
    siemplify = SiemplifyAction()

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "IP types found"  # human readable message, showed in UI as the action result
    result_value = "true"  # Set a simple result value, used for playbook if\else and placeholders.

    res = []
    to_enrich = []
    
    addresses = siemplify.parameters.get("IP Addresses")
    if addresses:
        addresses = addresses.split(",")
    try:
        for address in addresses:
            match = re.match(IPV4, address)
            if match:
                res.append({"Address": address, "IPType": "IPV4"})
            else:
                match = re.match(IPV6, address)
                if match:
                    res.append({"Address": address, "IPType": "IPV6"})
                else:
                    res.append({"Address": address, "IPType": "UNDETECTED"})
    
    
        for entity in siemplify.target_entities:
            if entity.entity_type == "ADDRESS":
                match = re.match(IPV4, entity.identifier)
                if match:
                    d = {"IPType": "IPV4"}
                else:
                    match = re.match(IPV6, entity.identifier)
                    if match:
                        d = {"IPType": "IPV6"}
                    else:
                        d = {"IPType": "UNDETECTED"}
                entity.additional_properties.update(d)
                to_enrich.append(entity)
                d["Address"] = entity.identifier
                res.append(d)


        if to_enrich:
            siemplify.update_entities(to_enrich)
        siemplify.result.add_result_json(res)
        siemplify.result.add_json("IP Types", res)
    except Exception as e:
        status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        result_value = False

    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)



if __name__ == "__main__":
    main()
