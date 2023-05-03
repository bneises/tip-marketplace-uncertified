from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED

# Example Consts:
INTEGRATION_NAME = "Tools"

SCRIPT_NAME = "Add Comment To Entity Log"

ADD_NOTE = "{}/external/v1/entities/AddNote?format=camel"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")

    comment = siemplify.extract_action_param(param_name="Comment", is_mandatory=True, print_value=True)
    user = siemplify.extract_action_param(param_name="User", is_mandatory=True, print_value=True)
    result_value = None
    output_message = ""
    status = EXECUTION_STATE_COMPLETED

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:

        for entity in siemplify.target_entities:
            siemplify.LOGGER.info("Adding comment to entity: {}".format(entity.identifier))

            payload = {"author": user, "content": comment, "entityIdentifier": entity.identifier, "id": 0,
                       "entityEnvironment": siemplify._environment}
            res = siemplify.session.post(ADD_NOTE.format(siemplify.API_ROOT), json=payload)
            siemplify.validate_siemplify_error(res)

            siemplify.LOGGER.info("Finished processing entity {0}".format(entity.identifier))
            output_message += "{} Added comment to entity: {}, Environment: {}. Comment: {}\n".format(user,
                                                                                                      entity.identifier,
                                                                                                      siemplify._environment,
                                                                                                      comment)

    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()