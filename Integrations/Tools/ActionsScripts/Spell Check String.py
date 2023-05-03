from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from spellchecker import SpellChecker
import re

@output_handler
def main():
    siemplify = SiemplifyAction()
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    json_result = {}
    spell = SpellChecker()
    input_string = siemplify.extract_action_param("String", default_value="", print_value=True)
    if input_string == "":
        result_value = 0
        output_message = "No input to test."
    else:
        json_result['input_string'] = input_string
        string_no_punctuation = re.sub("[^\w\s]", "", input_string)
        input_words = string_no_punctuation.split()
        json_result['total_words'] = len(input_words)

        misspelled = spell.unknown(input_words)
        json_result['total_misspelled_words'] = 0
        corrected = input_string
        json_result['misspelled_words'] = []
        for word in misspelled:
            correct = {'misspelled_word': word, 'correction': spell.correction(word)}
            if correct['misspelled_word'] != correct['correction']:
                json_result['total_misspelled_words'] += 1
                json_result['misspelled_words'].append(correct)
                corrected = re.sub(rf"\b{word}\b", correct['correction'], corrected)
        json_result['accuracy'] = int(
            (len(input_words) - json_result['total_misspelled_words']) / len(input_words) * 100)
        json_result['corrected_string'] = corrected
        result_value = json_result['accuracy']
        siemplify.result.add_result_json(json_result)
        output_message = f"The input string is {json_result['accuracy']}% accurate"
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()

