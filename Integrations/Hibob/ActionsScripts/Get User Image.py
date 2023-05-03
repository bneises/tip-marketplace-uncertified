from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from HibobManager import HibobManager, dict_to_flat
import base64, json

INTEGRATION_NAME = u"Hibob"


@output_handler
def main():
    siemplify = SiemplifyAction()

    #Extracting the integration params
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    api_root = 'https://api.hibob.com'
    api_token = conf.get("API Token")

    #Declaring an empty dictionary of the json_result
    json_result = {}
    
    #Creating an instance of hibobmanager object
    hibob_manager = HibobManager(api_root, api_token)
    
    #Extracting the action params
    user_email = siemplify.extract_action_param("Employee's Email")
    
    #Extracting the employee id(the employee id is a serial number that is generated automatically when creating the user)
    employee_details = hibob_manager.get_user_details(user_email)
    
    json_result = {}
    
    #If the user url is empty- returns false 
    if not employee_details :
        return_value = False
        json_result["exists"] = "False"
        json_result["imageBase64"] = "None"
        json_result["imageUrl"] = "None"
        output_message = "The user {0} was not found.".format(user_email)
        
    
    if employee_details:
        
        employee_identifier = employee_details.get('id')

        #Calling the function get_user_image() in the HibobManager
        # The function get_user_image() returns response.content
        user_image_url = hibob_manager.get_user_image(employee_identifier)

        if not user_image_url:
            return_value = False
            json_result["exists"] = "True"
            json_result["imageBase64"] = "None"
            json_result["imageUrl"] = "None"
            output_message = "The user {0} doesn't have an image.".format(user_email) 
            
        else:
            #Converting the user image to base64
            image_converted_to_base64 = (base64.b64encode(user_image_url))
            image_base64_string = image_converted_to_base64.decode('UTF-8')
            image_url_string = user_image_url.decode('UTF-8')
            
            return_value = True
            json_result["exists"]= "True"
            json_result["imageBase64"] = image_base64_string
            json_result["imageUrl"] = image_url_string
    
            output_message = "The user image was fetched for {0}".format(user_email )

    #Adding json result to the action
    siemplify.result.add_result_json(json_result)
    
    #Siemplify end function
    siemplify.end(output_message, return_value)

    


if __name__ == "__main__":
    main()
