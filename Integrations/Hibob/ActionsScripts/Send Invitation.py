from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from HibobManager import HibobManager, dict_to_flat
import json

INTEGRATION_NAME = u"Hibob"


@output_handler
def main():
    siemplify = SiemplifyAction()
    
    #Getting the integration parameters
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    api_root = 'https://api.hibob.com'
    api_token = conf.get("API Token")

    #Creating an HibobManager object instance
    hibob_manager = HibobManager(api_root, api_token)
    

    #The welcome wizard serial number- created via hibob.
    welcome_wizard_name = siemplify.extract_action_param("Welcome Wizard Name")
    
    #Extracting the action params= The employee's email
    user_email= siemplify.extract_action_param("Employee's Email")
    
    #Extracting the employee id(the employee id is a serial number that is generated automatically when creating the user)
    employee_details = hibob_manager.get_user_details(user_email)
    
    json_result = {}
    
    
    if not employee_details:
        return_value = False
        json_result["exists"] = "False"
        json_result["invitationWasSent"] = "False"
        output_message = "The employee {0} doesn't exist in Hibob".format(user_email)
        
  
    if employee_details:
        #Extracting the employee invite status
        employee_invite_status = employee_details.get('state')

        #Extracting the employee id 
        employee_identifier = employee_details.get('id')
        
        if employee_invite_status == 'invited':
            return_value = False
            json_result["exists"] = "True"
            json_result["invitationWasSent"] = "False"
            output_message = " {0} was already invited to Hibob ".format(user_email)
        
        else:
            #Getting all the wizards details
            welcome_wizards_details = hibob_manager.get_summery_about_all_wizards()
    
            #Finding the wizard id of the wizard name written in the action params.
            for wizard in welcome_wizards_details['wizards']:
                if wizard['name'] == welcome_wizard_name:
                    welcome_wizard_id= wizard['id']
                
                    #calling the function invite_employee_to_hibob() in the HibobManager
            invitation_user_response = hibob_manager.invite_employee_to_hibob(employee_identifier, welcome_wizard_id)

            if invitation_user_response:
                return_value = True
                json_result["Does employee exists"] = "True"
                json_result["Invitation was sent"] = "True"
                json_result["wizardName"] = welcome_wizard_name
                json_result["wizardId"] = welcome_wizard_id
                output_message = "The invitation for {0} was sent successfully .".format(user_email)

        
    print(json_result)
    siemplify.result.add_result_json(json_result)
    siemplify.end(output_message, return_value)
    
    

if __name__ == '__main__':
    main()