from SiemplifyUtils import output_handler
import json
from SiemplifyAction import SiemplifyAction
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from ToolsCommon import parse_raw_message

# CONSTS
OPEN_PH_PARENTHASIS = "{"
CLOSE_PH_PARENTHASIS = "}"
PIPE = "|"


@output_handler
def main():
    siemplify = SiemplifyAction()
    output_message = "No insight created"
    result_value = False
    
    raw_message = siemplify.parameters.get("Message")
    
    try:
        successful_entities = []
        for entity in siemplify.target_entities:
            message = parse_raw_message(entity, raw_message)
            if message:# and found_anything:
                output_message = message
                siemplify.add_entity_insight(entity, message, triggered_by=siemplify.parameters.get("Triggered By", "Siemplify"))
                successful_entities.append(entity)
        
        if successful_entities:
            result_value = True
            output_message = "Insights added for:\n{}".format("\n".join([x.identifier for x in successful_entities]))
        
        siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)
        
    except Exception as e:
        raise
        siemplify.end("Errors found: {}".format(e), 'Failed', EXECUTION_STATE_FAILED)


if __name__ == '__main__':
    main()
    