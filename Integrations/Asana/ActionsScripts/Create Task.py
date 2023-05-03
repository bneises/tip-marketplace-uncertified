from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from AsanaManager import AsanaManager

IDENTIFIER = u"Asana"


@output_handler
def main():
    siemplify = SiemplifyAction()
    assignees_user_id = None
    personal_access_token = siemplify.extract_configuration_param(IDENTIFIER, "Token")
    base_url = siemplify.extract_configuration_param(IDENTIFIER, "Base URL")

    task_subject = siemplify.extract_action_param("Task Subject")
    task_assignees = siemplify.extract_action_param("Assignee")
    task_due_date = siemplify.extract_action_param("Due Date")
    task_description = siemplify.extract_action_param("Description")
    project_name = siemplify.extract_action_param("Project Name")

    # Creating an instance of AsanaManager object
    asana_manager = AsanaManager(personal_access_token, base_url)

    project_id = asana_manager.get_project_id(project_name)

    # Getting the Usr Unique ID
    if task_assignees:
        assignees_user_id = asana_manager.get_user_id(task_assignees)

    created_task = asana_manager.create_task(task_subject, project_id, task_description, assignees_user_id,
                                             task_due_date)

    if created_task['data'] is not None:
        output_message = f"The task was created successfully for project {project_name}"
        return_value = True

        # Adding the tasks URLs
        title = 'The task name: {0} , Due date: {1}'.format(created_task['data']['name'],
                                                            created_task['data']['due_on'])
        link = created_task['data']['permalink_url']
        siemplify.result.add_link(title, link)

    else:
        output_message = f"The task was not created"
        return_value = False

    # Adding json result to the action
    siemplify.result.add_result_json(created_task)

    siemplify.end(output_message, return_value)


if __name__ == "__main__":
    main()
