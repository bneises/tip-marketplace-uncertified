from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import construct_csv, add_prefix_to_dict, convert_dict_to_json_result_dict,output_handler
from HibobManager import HibobManager, dict_to_flat
import requests, json

INTEGRATION_NAME = u"Hibob"

#This action does not need to change any data at the third party, but instead enriching the entity data in siemplify
#Adding additional_properties to the entity in siemplify. 

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    #Extracting the integration params
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    #The api_root is the url of the integration :https://api.hibob.com/
    api_root = 'https://api.hibob.com'
    #The api_token generated from hibob site
    api_token = conf.get("API Token")
    
    #Creating an instance of hibobmanager object
    hibob_manager = HibobManager(api_root, api_token)
    
    #declaring an empty array  for the new data 
    enriched_entities = []
    
    #declaring an empty dictionary of the json_result
    json_result = {}
    
    #Extracting the action params.
    user_email = siemplify.extract_action_param("Employee's Email")

    #Calling the function get_user_details from HibobManager
    #This function( get_user_details) returns response.json()
    user_details = hibob_manager.get_user_details(user_email)

    if user_details :
        json_result[user_email] = user_details
        print(json.dumps(user_details))
        #siemplify.result.add_result_json(json_result)
        return_value = True
        output_message = "The user {0} was found.".format(user_email)

    else:
        return_value = False
        output_message = "The user {0} wasn't found.".format(user_email)

    siemplify.result.add_result_json(json_result)
    
    siemplify.end(output_message, return_value)


if __name__ == '__main__':
    main()