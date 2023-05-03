from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import flat_dict_to_csv, construct_csv, dict_to_flat, convert_dict_to_json_result_dict
from SiemplifyUtils import output_handler
from BanduraCyberManager import BanduraCyberManager
from TIPCommon import extract_configuration_param, extract_action_param
import json

# CONTS
INTEGRATION_NAME = "BanduraCyber"
SCRIPT_NAME = "Show Allowed Domain Lists"
ADDRESS = EntityTypes.ADDRESS

@output_handler
def main():
    json_results = {}
    entities_with_results = []
    result_value = False
    
    # Configuration.
    siemplify = SiemplifyAction()
    siemplify.script_name = u"{} - {}".format(INTEGRATION_NAME, SCRIPT_NAME)
    siemplify.LOGGER.info("================= Main - Param Init =================")

    # INIT INTEGRATION CONFIGURATION:
    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"API Root",
                                           is_mandatory=True, input_type=unicode)
    username = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Username",
                                           is_mandatory=True, input_type=unicode)
    password = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Password",
                                           is_mandatory=True, input_type=unicode)
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name=u"Verify SSL",
                                             default_value=False, input_type=bool)
                                             
    list_name = extract_action_param(siemplify, param_name=u"List Name", is_mandatory=False, input_type=unicode,
                                       print_value=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    
    bandura_cyber_manager = BanduraCyberManager(username=username, password=password, verify_ssl=verify_ssl)
    
    results = bandura_cyber_manager.show_allowed_domain_list(list_name=list_name)
    
    # Close the session
    bandura_cyber_manager.logout()
    
    if results:
        # Add original json as attachment
        siemplify.result.add_attachment("Bandura Allowed Domain Lists Output", "allowed_domain_lists.txt", json.dumps(results))
    
        # Add data table
        siemplify.result.add_data_table("Bandura Allowed Domain Lists", construct_csv(results))

        siemplify.result.add_result_json(results)
        output_message = 'Following Allowed Domain Lists were found.\n'
        result_value = True
    else:
        output_message = 'No Allowed Domain Lists were found.'
        result_value = False
        
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
