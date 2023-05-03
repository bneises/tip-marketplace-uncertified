from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, add_prefix_to_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT



def get_alert_entities(siemplify):
    return [entity for alert in siemplify.case.alerts for entity in alert.entities]
    
@output_handler
def main():
    siemplify = SiemplifyAction()

    
    entity_type = siemplify.parameters.get("Entity Type")
    delimiter = siemplify.parameters.get("Entity Delimiter")
    enrichment_field = siemplify.parameters.get("Enrichment Field")
    enrichment_value = siemplify.parameters.get("Enrichment Value")
    
    target_entities = list(filter(None, [x.strip() for x in siemplify.parameters.get("List of Entities", "").split(delimiter)]))
    
    entities = []
    alert_entities = get_alert_entities(siemplify)
    for target_entity in target_entities:
        for entity in alert_entities:
            if entity.identifier.upper() == target_entity.upper() and entity.entity_type == entity_type:
                entities.append(entity)
                break
                    
    
    updated_entities = []        
    for entity in entities:
        entity.additional_properties[enrichment_field] = enrichment_value
        updated_entities.append(entity)
        
    count_updated_entities = len(updated_entities)
    
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)

    siemplify.end('{0} entities were successfully enriched'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
