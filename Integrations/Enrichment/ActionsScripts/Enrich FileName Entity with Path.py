from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import os
import ntpath
import re


def get_filename_from_path(path):
    is_win = re.match("^[A-Za-z]:\\\\", path.strip())
    if is_win:
        (file_path, full_file_name) = ntpath.split(path)
    else:
        file_path, full_file_name = os.path.split(path)
    filename, file_extension = os.path.splitext(full_file_name)
    file_details = {}
    if file_path:
        file_details['file_name'] = full_file_name
        file_details['file_path'] = file_path
        file_details['file_extension'] = file_extension
        return file_details


@output_handler
def main():
    siemplify = SiemplifyAction()
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    json_results = {}
    entities_to_update = []
    for entity in siemplify.target_entities:
        try:
            file_details = get_filename_from_path(entity.identifier)
            if file_details:
                json_results[entity.identifier] = file_details
                entity.additional_properties.update(file_details)
                entities_to_update.append(entity)
        except Exception as e:
            output_message += "Entity {} was not able to be parsed.\n".format(entity.identifier)
    if entities_to_update:
        siemplify.LOGGER.info("Updating entities")
        siemplify.update_entities(entities_to_update)
        siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_results))

        output_message += 'The following entities were enriched: {0}'.format(
            ','.join([entity.identifier for entity in siemplify.target_entities])
        )

    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
