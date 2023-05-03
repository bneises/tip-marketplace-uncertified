from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_INPROGRESS
from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from TIPCommon import extract_configuration_param, extract_action_param, construct_csv, add_prefix_to_dict
from PulsediveManager import PulsediveManager
from constants import PROVIDER_NAME, INTEGRATION_NAME, SCAN_INDICATOR_SCRIPT_NAME, DEFAULT_COMMENTS_COUNT, \
    DATA_ENRICHMENT_PREFIX, RISK_SCORE, COMPLETED, SCAN_TYPE
from exceptions import PulsediveNotFoundException, ForceRaiseException
import sys
import json
from UtilsManager import get_entity_original_identifier, prepare_entity_for_manager


def start_operation(siemplify, manager, suitable_entities, scan_type):
    failed_entities, successful_entities, result_value = [], [], {"processing": {}}
    output_message = ''
    status = EXECUTION_STATE_INPROGRESS
    for entity in suitable_entities:
        siemplify.LOGGER.info("Started processing entity {}".format(get_entity_original_identifier(entity)))
        try:

            scan_id = manager.scan_indicator(indicator=get_entity_original_identifier(entity), scan_type=scan_type)

            # Fill json with every entity data
            result_value["processing"][get_entity_original_identifier(entity)] = scan_id
            successful_entities.append(entity)
            siemplify.LOGGER.info("Finished processing entity {}".format(get_entity_original_identifier(entity)))

        except Exception as e:
            if isinstance(e, ForceRaiseException):
                raise
            failed_entities.append(get_entity_original_identifier(entity))
            siemplify.LOGGER.error("An error occurred on entity {}".format(get_entity_original_identifier(entity)))
            siemplify.LOGGER.exception(e)
    
    if successful_entities:
        output_message += "Successfully submitted the following Indicators for analysis: \n {} \n" \
            .format(', '.join([get_entity_original_identifier(entity) for entity in successful_entities]))
        result_value = json.dumps(result_value)

    if failed_entities:
        output_message += "Action wasn’t able to submitted the following Indicators for analysis: \n {} \n" \
            .format(', '.join(failed_entities))

    if not successful_entities:
        output_message = "No Indicators were submitted for analysis"
        result_value = False
        status = EXECUTION_STATE_COMPLETED

    return output_message, result_value, status


def query_operation_status(siemplify, manager, task_analysis):
    result_value = {"processing": {}, "completed": {}}
    if task_analysis.get('completed'):
        siemplify.LOGGER.info("Completed IDs: {}".format(task_analysis.get('completed')))
        result_value["completed"].update(task_analysis.get("completed"))
    
    if task_analysis.get("processing"):
        for entity, scan_id in task_analysis.get("processing").items():
            try:
                results = manager.is_scan_report_ready(scan_id)
    
                if COMPLETED != results:
                    result_value["processing"][entity] = scan_id
                else:
                    result_value["completed"][entity] = scan_id
    
            except Exception as e:
                siemplify.LOGGER.error("An error occurred when checking status for indicator {}".format(entity))
                siemplify.LOGGER.exception(e)

    return 'In progress analysis count: {}, Completed: {}'.format(len(result_value.get('processing')),
                                                                    len(result_value.get('completed'))), result_value
    

def finish_operation(siemplify, manager, suitable_entities, completed_scan_ids):
    global_is_risky = False
    successful_entities = []
    failed_entities = []
    not_found_engines = set()
    json_results = {}
    result_value = True
    comments = []
    output_message = ''
    only_suspicious_insight = extract_action_param(siemplify, param_name="Only Suspicious Entity Insight",
                                                   is_mandatory=False, input_type=bool, default_value=False)
    threshold = extract_action_param(siemplify, param_name="Threshold", is_mandatory=True, print_value=True)
    retrieve_comments = extract_action_param(siemplify, param_name="Retrieve Comments", is_mandatory=False,
                                             input_type=bool)
    max_returned_comments = extract_action_param(siemplify, param_name="Max Comments To Return", is_mandatory=False,
                                                 input_type=int, default_value=DEFAULT_COMMENTS_COUNT)

    for entity in suitable_entities:
        siemplify.LOGGER.info("Started processing entity: {}".format(get_entity_original_identifier(entity)))
        siemplify.LOGGER.info(completed_scan_ids)

        try:
            identifier = get_entity_original_identifier(entity)
            is_risky = False
            for scan_entity, scan_id in completed_scan_ids.items():
                siemplify.LOGGER.info("Here are the two entities to compare: {} {}".format(identifier, scan_entity))
                if identifier == scan_entity:
                    scan_data = manager.get_scan_indicator_data(indicator=identifier, 
                                                                retrieve_comments=retrieve_comments,
                                                                comment_limit=max_returned_comments, 
                                                                completed_scan_id=scan_id)
            
                    if int(RISK_SCORE.get(scan_data.threshold)) >= int(RISK_SCORE.get(threshold)):
                        is_risky = True
                        entity.is_suspicious = True
                        global_is_risky = True
                    
                    # Enrich entity
                    enrichment_data = scan_data.to_enrichment_data()
                    entity.additional_properties.update(enrichment_data)

                    # Fill json with every entity data
                    json_results[get_entity_original_identifier(entity)] = scan_data.to_json(comments=comments)
                    
                    # Create case wall table for comments
                    if scan_data.comments:
                        comments_table = construct_csv([comment.to_table() for comment in scan_data.comments])
                        siemplify.result.add_data_table(title="Comments: {}".format(get_entity_original_identifier(entity)),
                                                        data_table=comments_table)
        
                    if not only_suspicious_insight or (only_suspicious_insight and is_risky):
                        siemplify.add_entity_insight(entity, scan_data.to_insight(threshold),
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
        output_message += "Successfully enriched the following entities using  {}: \n {} \n" \
            .format(PROVIDER_NAME,
                    ', '.join([get_entity_original_identifier(entity) for entity in successful_entities]))
        siemplify.update_entities(successful_entities)

    if failed_entities:
        output_message += "Action wasn’t able to enrich the following entities using {}: \n {} \n" \
            .format(PROVIDER_NAME, ', '.join(failed_entities))

    if not_found_engines:
        output_message += "The following whitelisted engines were not found in {}: \n{} \n" \
            .format(PROVIDER_NAME, ', '.join(list(not_found_engines)))

    if not successful_entities:
        output_message = "No entities were enriched"
        result_value = False

    # Main JSON result
    if json_results:
        result = {
            'results': convert_dict_to_json_result_dict(json_results),
            'is_risky': global_is_risky
        }
        siemplify.result.add_result_json(result)

    return output_message, result_value, EXECUTION_STATE_COMPLETED


@output_handler
def main(is_first_run):
    siemplify = SiemplifyAction()
    siemplify.script_name = SCAN_INDICATOR_SCRIPT_NAME

    mode = "Main" if is_first_run else "Get Report"
    siemplify.LOGGER.info("----------------- {} - Param Init -----------------".format(mode))

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root")
    api_key = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Key")
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             default_value=True, input_type=bool)
                                             
    scan_type = extract_action_param(siemplify, param_name="Scan Type", is_mandatory=False, print_value=True, 
                                     default_value="Passive")

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    status = EXECUTION_STATE_COMPLETED

    suitable_entities = [entity for entity in siemplify.target_entities]
    result_value, output_message = False, ''
    
    try:
        finalize = False
        manager = PulsediveManager(api_root=api_root, api_key=api_key, verify_ssl=verify_ssl)
        
        if is_first_run:
            output_message, result_value, status = start_operation(siemplify=siemplify, manager=manager,
                                                                    suitable_entities=suitable_entities,
                                                                    scan_type=SCAN_TYPE.get(scan_type))
    
        task_analysis_json = result_value if result_value else extract_action_param(siemplify,
                                                                                    param_name="additional_data",
                                                                                    default_value='{}')
        task_analysis = json.loads(task_analysis_json)
        output_message, result_value = query_operation_status(siemplify=siemplify, manager=manager,
                                                              task_analysis=task_analysis)
        # if not remained analysis, we can finalize the action
        if len(result_value.get("processing")) == 0:
            finalize = True
        else:
            result_value = json.dumps(result_value)
        
        if finalize:
            siemplify.LOGGER.info(result_value)
            output_message, result_value, status = finish_operation(siemplify=siemplify, manager=manager,
                                                                    suitable_entities=suitable_entities, 
                                                                    completed_scan_ids=result_value.get('completed'))
    
    except Exception as err:
        output_message = "Error executing action “Scan Indicator”. Reason: {}".format(err)
        result_value = False
        status = EXECUTION_STATE_FAILED
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(err)

    siemplify.LOGGER.info('----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(
        "\n  status: {}\n  is_success: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    is_first_run = len(sys.argv) < 3 or sys.argv[2] == "True"
    main(is_first_run)
