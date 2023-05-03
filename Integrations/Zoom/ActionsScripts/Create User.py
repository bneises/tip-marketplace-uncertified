from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ZoomManager import ZoomManager

from parameters import Parameters


INTEGRATION_NAME = "Zoom"
SCRIPT_NAME = "Create User"


@output_handler
def main():

    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    # Extracting the integration params
    siemplify.LOGGER.info("------------------ Main Started -------------------")

    conf = siemplify.get_configuration(INTEGRATION_NAME)
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    parameters = Parameters.from_conf(conf)

    # Extracting the action params

    first_name = siemplify.extract_action_param("First Name")

    last_name = siemplify.extract_action_param("Last Name")

    user_email = siemplify.extract_action_param("Email")

    user_type = siemplify.extract_action_param("User Type")
    try:
        # Creating a ZoomManager object instance
        zoom_manager = ZoomManager(**parameters.as_dict(), logger=siemplify.LOGGER)

        json_result = {}

        created_user_details = zoom_manager.create_user(
            first_name, last_name, user_email, user_type
        )

        if created_user_details:
            json_result["createdUserDetails"] = created_user_details
            output_message = "The user was created successfully"
            result_value = True
            status = EXECUTION_STATE_COMPLETED
        else:
            output_message = "The user wasn't created"
            result_value = False
            status = EXECUTION_STATE_FAILED

        # Adding json result to the action
        siemplify.result.add_result_json(json_result)

        siemplify.LOGGER.info(
            "Script execution completed: \n"
            f"    Output message: {output_message} \n"
            f"    Result value: {result_value} \n"
        )

    except Exception as e:
        output_message = f"The user wasn't created: {e}"
        result_value = False
        status = EXECUTION_STATE_FAILED

    finally:
        siemplify.end(output_message, result_value, status)

        if status is EXECUTION_STATE_FAILED:
            siemplify.LOGGER.error("Error trying to create a user")
            siemplify.LOGGER.exception(output_message)
            raise


if __name__ == "__main__":
    main()
