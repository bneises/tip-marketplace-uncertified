from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json

@output_handler
def main():
    siemplify = SiemplifyAction()
    updated_entities = []
    
    for entity in siemplify.target_entities:
        entity.is_suspicious = True
        updated_entities.append(entity)
    count_updated_entities = len(updated_entities)
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)

    siemplify.end('{0} entities were successfully were marked suspicious.'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
