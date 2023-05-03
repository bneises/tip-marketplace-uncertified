from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from SiemplifyUtils import get_domain_from_entity,convert_dict_to_json_result_dict, dict_to_flat, add_prefix_to_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import whois_alt
from tldextract import extract
import json
from ipwhois import IPWhois
import re
from IpLocation import DbIpCity

EXTEND_GRAPH_URL = '{}/external/v1/investigator/ExtendCaseGraph'

from datetime import date, datetime

def create_entity_with_relation(siemplify, new_entity, linked_entity):
        json_payload = {
            "caseId": siemplify.case_id,
            "alertIdentifier": siemplify.alert_id,
            "entityType": "DOMAIN",
            "isPrimaryLink": False,
            "isDirectional": False,
            "typesToConnect": [],
            "entityToConnectRegEx": "{}$".format(re.escape(linked_entity.upper())),
            "entityIdentifier": new_entity.upper()
        }
        payload = json_payload.copy()
        created_entity = siemplify.session.post(EXTEND_GRAPH_URL.format(siemplify.API_ROOT), json=json_payload)
        created_entity.raise_for_status()
        
def get_alert_entities(siemplify):
        return [entity for alert in siemplify.case.alerts for entity in alert.entities]        

 
def get_domain_from_string(identifier):
    reg = extract(identifier.lower())
    return reg.registered_domain
    
    
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
    
    

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = ""  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    siemplify.script_name = "Whois"
    create_entities = siemplify.extract_action_param("Create Entities", print_value=True).lower() == "true"
    age_threshold = siemplify.extract_action_param("Domain Age Threshold", print_value=True, default_value=0, input_type=int)
    json_result = {}
    updated_entities = []
    enriched_entities = {}
    for entity in siemplify.target_entities:
        if entity.entity_type == "ADDRESS":
            try:
                obj = IPWhois(entity.identifier)
                obj.lookup_rdap(depth=1)
                ip_whois = obj.lookup_rdap(depth=1)
                response = DbIpCity.get(entity.identifier, api_key='free')
                ip_whois['geo_lookup'] = json.loads(response.to_json())
                json_result[entity.identifier] = ip_whois
                enriched_entities[entity.identifier] = ip_whois
                result_value = "true"
            except Exception as e:
                print(e)
                pass
        else:
            try:
                domain = get_domain_from_string(entity.identifier)
                if domain:
                    whois_data = whois_alt.get_whois(domain)
                    if 'creation_date' in whois_data:
                        whois_data['age_in_days'] = int((datetime.now() - whois_data['creation_date'][0]).total_seconds() / 86400)
                    json_result[entity.identifier] = json.loads(json.dumps(whois_data, default=json_serial))
                    del whois_data['raw']
                    enriched_entities[entity.identifier] = json.loads(json.dumps(whois_data, default=json_serial))
                    result_value = "true"
                    if create_entities and domain.upper() != entity.identifier:
                        create_entity_with_relation(siemplify, domain, entity.identifier)
                        enriched_entities[domain] = json.loads(json.dumps(whois_data, default=json_serial))
                        json_result[domain] = json.loads(json.dumps(whois_data, default=json_serial))
                
            except whois_alt.shared.WhoisException as e:
                pass
        
    if enriched_entities:
        siemplify.load_case_data()
        alert_entities = get_alert_entities(siemplify)
        for new_entity in enriched_entities:
            for entity in alert_entities:
                if new_entity.strip() == entity.identifier.strip():
                    entity.additional_properties.update(add_prefix_to_dict(dict_to_flat(enriched_entities[new_entity]), "WHOIS"))
                    if ('age_in_days' in enriched_entities[new_entity] 
                        and enriched_entities[new_entity]['age_in_days'] < int(age_threshold) 
                        and int(age_threshold) != 0):
                            if create_entities and entity.entity_type == "DOMAIN":
                                entity.is_suspicious = True
                                
                            elif not create_entities:
                                entity.is_suspicious = True
                                siemplify.LOGGER.info(f"Marking {entity.identifier} as suspicious")
                    entity.is_enriched = True
                    updated_entities.append(entity)
                    break
        siemplify.LOGGER.info(f"updating entities: {updated_entities}")
        siemplify.update_entities(updated_entities)
        output_message += "Enriched the following entities {}".format(updated_entities)
            

    return_json = json.dumps(json_result, default=json_serial)
    siemplify.result.add_result_json(convert_dict_to_json_result_dict(return_json))
    
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()