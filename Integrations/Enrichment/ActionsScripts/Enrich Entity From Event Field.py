from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json


@output_handler
def main():
    siemplify = SiemplifyAction()



    fields = siemplify.parameters.get("Fields to enrich").split(',')
    event = siemplify.current_alert.security_events[0]
    fields_to_enrich = {}
    lower_dict = {k.lower(): v for k, v in event.additional_properties.items()}
    updated_entities = []
    
    for entity in siemplify.target_entities:
        entity_is_updated = False
        for field in fields:
            lower_field = field.lower()
            if lower_field in lower_dict:
                fields_to_enrich[lower_field] = lower_dict[lower_field]
                entity.additional_properties[lower_field] = lower_dict[lower_field]
                entity_is_updated = True
        if entity_is_updated == True:
            updated_entities.append(entity)
    
    count_updated_entities = len(updated_entities)
    
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)
    
    for updated_entity in updated_entities:
        siemplify.result.add_json(updated_entity.identifier, json.dumps(fields_to_enrich))

    siemplify.result.add_result_json(json.dumps(fields_to_enrich))
    siemplify.end('{0} entities were successfully were enriched'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
