from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import re

SCRIPT_NAME = "Search Text"

INTEGRATION = "Tools"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "No match was found in the input string."  # human readable message, showed in UI as the action result
    result_value = "false"  # Set a simple result value, used for playbook if\else and placeholders.
    json_result = {'matches': []}
    text = siemplify.extract_action_param("Text", "")
    search_for = siemplify.extract_action_param("Search For")
    case_sensitive = siemplify.parameters.get("Case Sensitive", "false").lower() == "true"
    search_for_regex = list(
        filter(None, [x.strip() for x in siemplify.extract_action_param("Search For Regex", "").split(',')]))

    if not search_for and not search_for_regex:
        status = EXECUTION_STATE_FAILED
        output_message = "Search For or Search For Regex must contain a value."
        result_value = "false"

    if search_for:
        if case_sensitive:
            if search_for in text:
                result_value = "true"
        else:
            if search_for.lower() in text.lower():
                result_value = "true"

        if result_value == "true":
            output_message = f"A match was found in the input string for {search_for}."
            match = {'search': search_for, 'input': text, 'match': True}
            json_result['matches'].append(match)

    if search_for_regex:
        for regex in search_for_regex:
            regex = regex.strip('"')
            if case_sensitive:
                found = re.search(regex, text, flags=re.M)
            else:
                found = re.search(regex, text, flags=re.I | re.M)
            if found:
                result_value = "true"
                output_message = f"A match was found in the input string using regex: {regex}."
                match = {'search': regex, 'input': text, 'match': True}
                json_result['matches'].append(match)
                # break
    siemplify.result.add_result_json(json_result)
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
