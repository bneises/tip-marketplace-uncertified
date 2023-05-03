from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from HibobManager import HibobManager
import base64

INTEGRATION_NAME = u"Hibob"

@output_handler
def main():
    siemplify = SiemplifyAction()

    #Getting the integration parameters
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    api_root = 'https://api.hibob.com'
    api_token = conf.get("API Token")

    #declaring an empty dictionary of the json_result
    json_result = {}
    
    #creating an instance of hibobmanager object
    hibob_manager = HibobManager(api_root, api_token)
    
    #Extracting the action params= The employee's email
    user_email = siemplify.extract_action_param("Employee's Email")
    
    #Extracting the action params= The employee's URL image
    url_image =  siemplify.extract_action_param("Url Image")
    
    #Extracting the employee id(the employee id is a serial number that is generated automatically when creating the user)
    employee_details = hibob_manager.get_user_details(user_email)
    
    if employee_details:
        employee_identifier = employee_details.get('id')
        user_image_url = hibob_manager.upload_user_image(employee_identifier, url_image)
    
    
        if user_image_url == 404:
            return_value = False
            output_message = "The image of {0} was not uploaded.".format(user_email)

        else:
            return_value = True
            output_message = "The image of {0} was uploaded successfully.".format(user_email)

    else:
        return_value = False
        output_message = "The user doesn't exists in Hibob"
        
    siemplify.result.add_result_json(json_result)
    
    siemplify.end(output_message, return_value)

    


if __name__ == "__main__":
    main()
