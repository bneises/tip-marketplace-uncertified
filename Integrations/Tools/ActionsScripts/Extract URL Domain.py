from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from SiemplifyDataModel import EntityTypes


import re
import json
from tldextract import extract

# Consts:
INTEGRATION_NAME = "Tools"
SCRIPT_NAME = "Tools_ExtractURLDomain"

DOMAON_REGEX = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'

#def get_domain_from_string(identifier):
#    reg = extract(identifier.lower())
#    return reg.registered_domain

def get_domain_from_string(identifier, extract_subdomain):
    reg = extract(identifier.lower())
    if extract_subdomain:
        if reg.subdomain != "":
            return '.'.join(reg[:3])
        else:
            return '.'.join(reg[1:3])
    else:
        return reg.registered_domain

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        status = EXECUTION_STATE_COMPLETED
        output_message = "No URLs processed"
        result_value = 0
        failed_entities = []
        successfull_entities = []
        json_result = {}
        out_message_list = []
        
        urls = siemplify.parameters.get("URLs")
        extract_subdomain = siemplify.extract_action_param("Extract subdomain", print_value=True).lower() == "true"
        
        if urls:
            separator = siemplify.parameters.get("Separator")
            for url in urls.split(separator):
                try:
                    domain = get_domain_from_string(url.strip(), extract_subdomain)
                    if domain:
                        out_message_list.append("Domain extracted for param URL {}".format(url))
                        json_result[url.strip()] = {"domain": domain, "source_entity_type": EntityTypes.URL }
                        result_value += 1
                except Exception as e:
                    out_message_list.append("Failed extracting domain for param URL {}".format(url))
                    json_result[url.strip()] = {"Error": "Exception: {}".format(e)}
                

        
        for entity in siemplify.target_entities:
            try:
                domain = get_domain_from_string(entity.identifier, extract_subdomain)
                if domain:
                    entity.additional_properties["siemplifytools_extracted_domain"] = domain
                    successfull_entities.append(entity)
                    json_result[entity.identifier] = {"domain": domain, "source_entity_type": entity.entity_type}
                else:
                    failed_entities.append(entity)
            except Exception as e:
                failed_entities.append(entity)
                json_result[entity.identifier] = {"Error": "Exception: {}".format(e)}
        
        
        
        if successfull_entities:
            siemplify.update_entities(successfull_entities)
            out_message_list.append("Domain extracted for {}".format([x.identifier for x in successfull_entities]))
            
        
        if failed_entities:
            out_message_list.append("Failed extracting domain for {}".format([x.identifier for x in failed_entities]))
        
        if json_result:
            siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_result))
        if out_message_list:
            output_message = "\n".join(out_message_list)
        
        result_value += len(successfull_entities)
    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = "Failed"
        output_message += "\n unknown failure"
        raise


    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
