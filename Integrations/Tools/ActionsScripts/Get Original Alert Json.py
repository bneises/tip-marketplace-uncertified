from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
import json
import uuid
import os


@output_handler
def main():
    try:
        siemplify = SiemplifyAction(get_source_file=True)
    except TypeError:
        siemplify = SiemplifyAction()

    case_data = json.loads(siemplify.current_alert.entities[0].additional_properties['SourceFileContent'])
    
    siemplify.result.add_result_json(case_data)
    
    siemplify.end("See technical details", json.dumps(case_data))


if __name__ == "__main__":
    main()

