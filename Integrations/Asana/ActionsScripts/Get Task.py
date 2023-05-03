from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from AsanaManager import AsanaManager

IDENTIFIER = u"Asana"


@output_handler
def main():
    siemplify = SiemplifyAction()

    personal_access_token = siemplify.extract_configuration_param(IDENTIFIER, "Token")
    base_url = siemplify.extract_configuration_param(IDENTIFIER, "Base URL")

    task_id = siemplify.extract_action_param("Task ID")

    # Creating an instance of AsanaManager object
    asana_manager = AsanaManager(personal_access_token, base_url)

    task_details = asana_manager.get_a_task(task_id)

    if task_details['data'] is not None:
        output_message = f"The task {task_id} was updated successfully"
        return_value = True
        # Adding the tasks URLs
        title = 'The task name: {0} , Due date: {1}'.format(task_details['data']['name'],
                                                            task_details['data']['due_on'])
        link = task_details['data']['permalink_url']
        siemplify.result.add_link(title, link)

    else:
        output_message = f"The task {task_id} wasn't found"
        return_value = False
    # Adding json result to the action
    siemplify.result.add_result_json(task_details)

    siemplify.end(output_message, return_value)


if __name__ == "__main__":
    main()
