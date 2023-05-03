from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from HibobManager import HibobManager

INTEGRATION_NAME = u"Hibob"

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    #Extracting the integration params
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    api_root = 'https://api.hibob.com'
    api_token = conf.get("API Token")

    #Creating an instance of hibobmanager object
    hibob_manager = HibobManager(api_root, api_token)
    
    #Calling the function test_connectivity() from the HibobManager
    # This function test_connectivity() returns boolean value
    response = hibob_manager.test_connectivity()

    if not response:
        return_value = False
        output_message = 'The Connection failed'
    
    else:
        return_value = True
        output_message = 'Connected successfully'
        
    # Test connectivity
    siemplify.end(output_message, return_value)

    


if __name__ == "__main__":
    main()
