from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json


@output_handler
def main():
    siemplify = SiemplifyAction()


    json_data = siemplify.parameters.get("Fields to enrich")
    fields_to_enrich = json.loads(json_data)

    updated_entities = []
    
    for entity in siemplify.target_entities:
        for field in fields_to_enrich:
            entity.additional_properties[field['entity_field_name']] = field['entity_field_value']
        updated_entities.append(entity)
        
    count_updated_entities = len(updated_entities)
    
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)
    
    for updated_entity in updated_entities:
        siemplify.result.add_json(updated_entity.identifier, json.dumps(fields_to_enrich))

    siemplify.end('{0} entities were successfully were enriched'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
