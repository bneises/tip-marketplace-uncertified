from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json


@output_handler
def main():
    siemplify = SiemplifyAction()

    json_data = siemplify.parameters.get("Normalization Data")
    enrichment_data = json.loads(json_data)

    updated_entities = []
    
    for entity in siemplify.target_entities:
        for pair in enrichment_data:
            if pair['entitiy_field_name'] in entity.additional_properties:
                entity.additional_properties[pair['new_name']] = entity.additional_properties.get(pair['entitiy_field_name'], "NotFound")
            else: # field does not exist
                if pair['new_name'] not in entity.additional_properties: # Normalized key does not exist yet anyway
                    entity.additional_properties[pair['new_name']] = ""  # No key anyway, we put empty string
        updated_entities.append(entity)
        
    count_updated_entities = len(updated_entities)
    
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)
    
    

    siemplify.end('{0} entities were successfully were enriched'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
