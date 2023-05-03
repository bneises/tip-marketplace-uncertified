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

    workspace_name = siemplify.extract_action_param("Workspace Name")
    user_to_remove = siemplify.extract_action_param("User's Email")

    # Creating an instance of AsanaManager object
    asana_manager = AsanaManager(personal_access_token, base_url)

    workspace_id = asana_manager.get_workspace_id_by_name(workspace_name)

    removed_user_from_workspace = asana_manager.remove_user_from_workspace(workspace_id, user_to_remove)

    if removed_user_from_workspace['data'] is not None:
        output_message = f"The user {user_to_remove} was removed from the workspace: {workspace_name} successfully"
        return_value = True

    else:
        output_message = f"The user {user_to_remove} wasn't removed from the workspace: {workspace_name} "
        return_value = False

    siemplify.end(output_message, return_value)


if __name__ == "__main__":
    main()
