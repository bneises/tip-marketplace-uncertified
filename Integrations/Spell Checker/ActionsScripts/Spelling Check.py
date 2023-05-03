from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from SiemplifyDataModel import EntityTypes

from SpellCheckerManager import SpellCheckerManager

import json
from functools import reduce
import re

# Consts:
INTEGRATION_NAME = "Spell Checker"
SCRIPT_NAME = "Spelling Check"



@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    try:
        status = EXECUTION_STATE_COMPLETED
        output_message = "output message :"
        result_value = 0
        failed_entities = []
        successfull_entities = []
        
        result_json = {}
        spm = SpellCheckerManager()
        input_text = siemplify.parameters.get("Input")
        input_text = re.sub(r'[\(\)\r\n,]+', ' ',
                                    re.sub(r'[^A-Za-z\s\(\)@]+', '', input_text))
        # raise Exception(json.dumps([x.strip() for x in input_text.split(" ") if x.strip()], indent=4))
        res = spm.spell.unknown([x.strip() for x in input_text.split(" ") if x.strip() and '@' not in x and not 'http' in x])
        
        for item in res:
            result_json[item] = list(spm.spell.candidates(item))
        if result_json:
            siemplify.result.add_result_json(convert_dict_to_json_result_dict(result_json))
            result_value = len(result_json)
            
            # Build table result:
            csv_table = ["Original text ,Recommended corrections"]
            for bad_word, correction_list in result_json.items():
                csv_table.append("{},{}".format(bad_word, u"\u2E41 ".join(correction_list)))
            siemplify.result.add_data_table("Found spelling mistakes", csv_table)
            
        # print(result_json)
        output_message = u"Found {} mistakes/errors in the text".format(result_value)

    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED
        result_value = -1
        output_message += "\n unknown failure"
        raise

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
