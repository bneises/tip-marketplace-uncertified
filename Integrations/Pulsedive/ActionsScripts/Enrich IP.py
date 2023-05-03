from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_INPROGRESS
from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from TIPCommon import extract_configuration_param, extract_action_param, construct_csv, add_prefix_to_dict
from PulsediveManager import PulsediveManager
from constants import PROVIDER_NAME, INTEGRATION_NAME, ENRICH_IP_SCRIPT_NAME, DEFAULT_COMMENTS_COUNT, \
    DATA_ENRICHMENT_PREFIX, RISK_SCORE, RISK_NAME, COMPLETED
from exceptions import PulsediveNotFoundException, ForceRaiseException
import sys
import json
from UtilsManager import get_entity_original_identifier, prepare_entity_for_manager


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ENRICH_IP_SCRIPT_NAME

    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root")
    api_key = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Key")
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             default_value=True, input_type=bool)
                                        
    retrieve_comments = extract_action_param(siemplify, param_name="Retrieve Comments", is_mandatory=False,
                                                 input_type=bool)
    max_returned_comments = extract_action_param(siemplify, param_name="Max Comments To Return", is_mandatory=False,
                                                 input_type=int, default_value=DEFAULT_COMMENTS_COUNT)
    only_suspicious_insight = extract_action_param(siemplify, param_name="Only Suspicious Entity Insight",
                                                   is_mandatory=False, input_type=bool, default_value=False)
    threshold = extract_action_param(siemplify, param_name="Threshold", is_mandatory=True, print_value=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    global_is_risky = False
    successful_entities = []
    failed_entities = []

    status = EXECUTION_STATE_COMPLETED
    json_results = {}
    result_value = "false"
    output_message = ''

    suitable_entities = [entity for entity in siemplify.target_entities if entity.entity_type == EntityTypes.ADDRESS]
    result_value, output_message = False, ''

    try:
        manager = PulsediveManager(api_root=api_root, api_key=api_key, verify_ssl=verify_ssl)

        for entity in suitable_entities:
            siemplify.LOGGER.info("Started processing entity: {}".format(get_entity_original_identifier(entity)))
            
            try:
                identifier = get_entity_original_identifier(entity)
                is_risky = False
                ip_data = manager.get_indicator_data(indicator=identifier, retrieve_comments=retrieve_comments,
                                                      comment_limit=max_returned_comments)
    
                if int(RISK_SCORE.get(ip_data.threshold)) >= int(RISK_SCORE.get(RISK_NAME.get(threshold))):
                    is_risky = True
                    entity.is_suspicious = True
                    global_is_risky = True
                
                # Enrich entity
                enrichment_data = ip_data.to_enrichment_data()
                entity.additional_properties.update(enrichment_data)
    
                # Fill json with every entity data
                json_results[get_entity_original_identifier(entity)] = ip_data.to_json(comments=ip_data.comments)
                
                # Create case wall table for comments
                if ip_data.comments:
                    comments_table = construct_csv([comment.to_table() for comment in ip_data.comments])
                    siemplify.result.add_data_table(title="Comments: {}".format(get_entity_original_identifier(entity)),
                                                    data_table=comments_table)
    
                if not only_suspicious_insight or (only_suspicious_insight and is_risky):
                    siemplify.add_entity_insight(entity, ip_data.to_insight(threshold),
                                                 triggered_by=INTEGRATION_NAME)
    
                entity.is_enriched = True
                successful_entities.append(entity)
                siemplify.LOGGER.info("Finished processing entity {0}".format(get_entity_original_identifier(entity)))
    
            except Exception as e:
                if isinstance(e, ForceRaiseException):
                    raise
                failed_entities.append(get_entity_original_identifier(entity))
                siemplify.LOGGER.error("An error occurred on entity {0}".format(get_entity_original_identifier(entity)))
                siemplify.LOGGER.exception(e)
    
        if successful_entities:
            output_message += "Successfully enriched the following IPs using {}: \n {} \n" \
                .format(PROVIDER_NAME,
                        ', '.join([get_entity_original_identifier(entity) for entity in successful_entities]))
            siemplify.update_entities(successful_entities)
    
        if failed_entities:
            output_message += "Action wasn’t able to enrich the following IPs using {}: \n {} \n" \
                .format(PROVIDER_NAME, ', '.join(failed_entities))
    
        if not successful_entities:
            output_message = "No IPs were enriched"
            result_value = False
    
        # Main JSON result
        if json_results:
            result = {
                'results': convert_dict_to_json_result_dict(json_results),
                'is_risky': global_is_risky
            }
            siemplify.result.add_result_json(result)
    except Exception as err:
        output_message = "Error executing action “Enrich IP”. Reason: {}".format(err)
        result_value = False
        status = EXECUTION_STATE_FAILED
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(err)

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("Status: {}:".format(status))
    siemplify.LOGGER.info("Result Value: {}".format(result_value))
    siemplify.LOGGER.info("Output Message: {}".format(output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
