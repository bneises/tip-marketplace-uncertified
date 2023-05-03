from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_INPROGRESS
from Siemplify import InsightSeverity, InsightType
from SiemplifyAction import SiemplifyAction
from SiemplifyDataModel import EntityTypes
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from TIPCommon import extract_configuration_param, extract_action_param, construct_csv, add_prefix_to_dict
from PulsediveManager import PulsediveManager
from constants import PROVIDER_NAME, INTEGRATION_NAME, GET_THREAT_SCRIPT_NAME, DEFAULT_COMMENTS_COUNT, \
    DATA_ENRICHMENT_PREFIX, RISK_SCORE, RISK_NAME, COMPLETED, IN_PROGRESS
from exceptions import PulsediveNotFoundException, ForceRaiseException, PulsediveLimitReachedException
import sys
import json
from UtilsManager import get_entity_original_identifier, prepare_entity_for_manager


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = GET_THREAT_SCRIPT_NAME

    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Root")
    api_key = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="API Key")
    verify_ssl = extract_configuration_param(siemplify, provider_name=INTEGRATION_NAME, param_name="Verify SSL",
                                             default_value=True, input_type=bool)
                                             
    threat_name = extract_action_param(siemplify, param_name="Threat Name", is_mandatory=False,
                                                 input_type=str)
    threat_id = extract_action_param(siemplify, param_name="Threat ID",
                                                   is_mandatory=False, input_type=str)
    split_risk = extract_action_param(siemplify, param_name="Split Risk", is_mandatory=False,
                                                 input_type=bool)
    retrieve_comments = extract_action_param(siemplify, param_name="Retrieve Comments", is_mandatory=False,
                                                 input_type=bool)
    create_insight = extract_action_param(siemplify, param_name="Create Insight", is_mandatory=False,
                                                 input_type=bool)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    status = EXECUTION_STATE_COMPLETED
    json_results = {}
    result_value = "false"
    output_message = ""
    threat_data = {}

    result_value, output_message = False, ''

    try:
        manager = PulsediveManager(api_root=api_root, api_key=api_key, verify_ssl=verify_ssl)

        siemplify.LOGGER.info("Started processing threat: {}".format(threat_name if threat_name else threat_id))
        try:
            if threat_name: 
                threat_data = manager.get_threats(threat_name=threat_name,
                                                  retrieve_comments=retrieve_comments,
                                                  split_risk=split_risk)
            elif threat_id: 
                threat_data = manager.get_threats(threat_id=threat_id,
                                                  retrieve_comments=retrieve_comments,
                                                  split_risk=split_risk)
            else:
                raise
            
            if threat_data:
                result_value = True
                
                # Create case wall table for comments
                if threat_data.threat_comments:
                    comments_table = construct_csv([comment.to_table() for comment in threat_data.threat_comments])
                    siemplify.result.add_data_table(title="Comments: {}".format(threat_data.threat_name),
                                                    data_table=comments_table)
                
                # Fill json with every entity data
                json_results[threat_data.threat_name] = threat_data.to_json(comments=threat_data.threat_comments,
                                                                            news=threat_data.threat_news)
    
                if create_insight:
                    siemplify.create_case_insight(
                        triggered_by=INTEGRATION_NAME,
                        title="Threat Details",
                        content=threat_data.to_insight(),
                        entity_identifier=threat_data.threat_name,
                        severity=InsightSeverity.INFO,
                        insight_type=InsightType.General)
            else:
                output_message = "No threat details were retrieved."
                result_value = False
            
            siemplify.LOGGER.info("Finished processing threat {0}".format(threat_data.threat_name))
            
        except Exception as e:
            if isinstance(e, ForceRaiseException):
                raise
            if isinstance(e, PulsediveNotFoundException):
                output_message = "No threat details found."
            if isinstance(e, PulsediveLimitReachedException):
                output_message = "Pulsedive limit exceeded."
                
            siemplify.LOGGER.error("An error occurred on threat name/id {0}".format(threat_name))
            siemplify.LOGGER.exception(e)

        if json_results:
            output_message = "Successfully retrieved threat details for:\n{}".format(
                threat_name if threat_name else threat_id)
            result = {
                'results': convert_dict_to_json_result_dict(json_results),
            }
            siemplify.result.add_result_json(result)
                                                                    
    except Exception as err:
        output_message = "Error executing action “Get Threat Details”. Reason: {}".format(err)
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
