from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json
import time
from ToolsCommon import parse_version_string_to_tuple, is_supported_siemplify_version
from datetime import datetime

X5_TASK_URL = '{}/external/v1/cases/AddOrUpdateCaseTask'
X6_TASK_URL = '{}/external/v1/dynamic-cases/AddOrUpdateCaseTask'
ACTION_NAME = "CreateNewTask"
CREATE_TASK_SIEMPLIFY_5X_VERSION = "5.0.0.0"
CREATE_TASK_SIEMPLIFY_6X_VERSION = "6.0.0.0"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME

    assign_to = siemplify.extract_action_param(param_name="Assign To", is_mandatory=True, print_value=True)
    task_content = siemplify.extract_action_param(param_name="Task Content", is_mandatory=True, print_value=True)
    duration = siemplify.extract_action_param(param_name="SLA (in minutes)", is_mandatory=True, print_value=True)
    task_title = siemplify.extract_action_param(param_name="Task Title", is_mandatory=False, print_value=True)

    time_now = datetime.now()
    time_now_epoch = int(time.mktime(time_now.timetuple())) * 1000
    client_time = time_now_epoch + (int(duration) * 1000 * 60)
    case_id = siemplify.case_id

    current_version = siemplify.get_system_info(int(time.time()))["version_number"]
    siemplify.LOGGER.info(u"Siemplify Platform version is {}".format(current_version))
    json_payload = {}
    task_url = ""

    if is_supported_siemplify_version(parse_version_string_to_tuple(current_version),
                                      parse_version_string_to_tuple(CREATE_TASK_SIEMPLIFY_6X_VERSION)):
        json_payload = {"owner": assign_to,
                        "content": task_content,
                        "dueDate": "",
                        "dueDateUnixTimeInMs": client_time,
                        "title": task_title,
                        "caseId": case_id}
        task_url = X6_TASK_URL
    elif is_supported_siemplify_version(parse_version_string_to_tuple(current_version),
                                        parse_version_string_to_tuple(CREATE_TASK_SIEMPLIFY_5X_VERSION)):
        json_payload = {"owner": assign_to, "name": task_content, "dueDate": "", "dueDateUnixTimeMs": client_time,
                        "caseId": case_id}
        task_url = X5_TASK_URL

    add_task = siemplify.session.post(task_url.format(siemplify.API_ROOT), json=json_payload)
    add_task.raise_for_status()

    output_message = "A new task has been created for the user: {0}.\nThis task should be handled in the next {1} mintues".format(
        assign_to, duration)
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()