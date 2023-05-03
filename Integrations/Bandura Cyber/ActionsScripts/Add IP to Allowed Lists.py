from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import flat_dict_to_csv, construct_csv, dict_to_flat, convert_dict_to_json_result_dict
from SiemplifyUtils import output_handler
from BanduraCyberManager import BanduraCyberManager
from TIPCommon import extract_configuration_param, extract_action_param

# CONTS
INTEGRATION_NAME = "BanduraCyber"
SCRIPT_NAME = "Add IP to Allowed Lists"
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
                                             
    list_name = extract_action_param(siemplify, param_name=u"List Name", is_mandatory=True, input_type=unicode,
                                       print_value=True)
    description = extract_action_param(siemplify, param_name=u"Description", is_mandatory=False, input_type=unicode,
                                       print_value=True)
    maskbit = extract_action_param(siemplify, param_name=u"Maskbit", is_mandatory=False, input_type=int,
                                       print_value=True, default_value=32)
    expiration_date = extract_action_param(siemplify, param_name=u"Expiration Date", is_mandatory=False, input_type=unicode,
                                       print_value=True, default_value="")
    

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    
    bandura_cyber_manager = BanduraCyberManager(username, password, verify_ssl=verify_ssl)
    
    # Get scope entities.
    scope_entities = [entity for entity in siemplify.target_entities if entity.entity_type == ADDRESS]
    
    for entity in scope_entities:
        siemplify.LOGGER.info(u"Processing entity {}".format(entity.identifier))
        siemplify.LOGGER.info(u"Adding {} to {} Allowed List".format(entity.identifier, list_name))
        results = bandura_cyber_manager.add_allowed_ip_entity(list_name, entity.identifier, 
                                                              maskbit, description, expiration_date)

        if results:
            json_results[entity.identifier] = results[0]
            entities_with_results.append(entity.identifier)
            result_value = True

    if result_value:
        output_message = u'Added the following Entities to {0}: {1}'.format(list_name, ', '.join(entities_with_results))
    else:
        output_message = u'No entities were added'

    siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_results))
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
