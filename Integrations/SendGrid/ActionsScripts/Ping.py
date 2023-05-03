from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes
from SiemplifyAction import SiemplifyAction
import http.client
import json
import re

INTEGRATION_NAME = "SendGrid"
SCRIPT_NAME = "sendgrid_ping"

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    siemplify.script_name = SCRIPT_NAME
    output_message = ""
    
    configurations = siemplify.get_configuration('SendGrid')
    api_token = configurations['API Token']
    
    result_value = False
    
    conn = http.client.HTTPSConnection("api.sendgrid.com")
    
    payload = "{}"
    headers = {}
    headers['authorization'] = "Bearer {}".format(api_token)
    
    conn.request("GET", "/v3/scopes", payload, headers)
    
    result_value = False

    try:
        response = conn.getresponse()
        data = response.read()
        
        val_decoded = data.decode("utf-8")
        val_json = json.loads(val_decoded)
        sendgrid_permission = str(val_json["scopes"])
        
        match_output = re.search(r"\bmail.send\b", sendgrid_permission)
        
        if (match_output is None ):
            output_message = "Error - {}".format("Unable to connect to SendGrid")
            result_value = False
        else:
            output_message = "Successfully connected to SendGrid - valid token"
            result_value = True
            
            
    except Exception as e:
        #siemplify.LOGGER.error(e)
        output_message = "Error - {}".format("Unable to connect to SendGrid")
    
    print(output_message)
    siemplify.end(output_message, result_value)
    

if __name__ == '__main__':
	main()