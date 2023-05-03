from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import socket, struct

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


@output_handler
def main():
    siemplify = SiemplifyAction()

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    
    ip_addresses = list(filter(None, [x.strip() for x in siemplify.parameters.get("IP Addresses").split(',')]))
    json_result = {}
    res = []
    for ip_addr in ip_addresses:
        
        iplong = ip2long(ip_addr)
        print(iplong)
        json_result[ip_addr] = iplong
        res.append(iplong)
    
    siemplify.result.add_result_json(json_result)
    
    result_value = ",".join(map(str, res))
    output_message = f"Converted from: {ip_addresses} to {result_value}"

    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
