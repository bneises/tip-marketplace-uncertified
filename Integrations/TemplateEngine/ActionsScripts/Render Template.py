from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from jinja2 import Template, Environment
import JinjaFilters
import json
import dateutil
import time
from inspect import getmembers, isfunction

# Example Consts:
INTEGRATION_NAME = "TemplateEngine"

SCRIPT_NAME = "RenderTemplate"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")

    events = []
    for event in siemplify.current_alert.security_events:
        events.append(event.additional_properties)
    entities = {}
    for entity in siemplify.target_entities:
        if entity.additional_properties["Type"] != "ALERT":
            entities[entity.additional_properties["Identifier"]] = entity.additional_properties

    # INIT ACTION PARAMETERS:
    json_object = siemplify.extract_action_param(param_name="JSON Object", is_mandatory=False, print_value=False,
                                                 default_value="{}")
    template = siemplify.extract_action_param(param_name="Template", is_mandatory=False, print_value=False)
    jinja = siemplify.extract_action_param(param_name="Jinja", is_mandatory=False, print_value=False)
    include_case_data = str(
        siemplify.extract_action_param(param_name="Include Case Data", is_mandatory=False, print_value=False,
                                       default_value='true')).lower() == 'true'
    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
        output_message = "output message :"  # human readable message, showed in UI as the action result
        result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
        try:
            input_json = json.loads(json_object)


        except Exception as e:
            siemplify.LOGGER.error("Error parsing JSON Object: {}".format(json_object))
            siemplify.LOGGER.exception(e)
            raise
            status = EXECUTION_STATE_FAILED
            result_value = "Failed"
            output_message += "\n failure parsing JSON object."
        jinja_env = Environment(autoescape=True, extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
                                trim_blocks=True, lstrip_blocks=True)
        filters = {name: function
                   for name, function in getmembers(JinjaFilters)
                   if isfunction(function)}

        jinja_env.filters.update(filters)

        try:
            import CustomFilters
            custom_filters = {name: function
                   for name, function in getmembers(CustomFilters)
                   if isfunction(function)}
            jinja_env.filters.update(custom_filters)
        except Exception as e:
            siemplify.LOGGER.info("Unable to load CustomFilters")
            siemplify.LOGGER.info(e)
            pass
        

        if type(input_json) == list:
            result_value = ''
            if jinja:
                template = jinja_env.from_string(jinja)
            else:
                template = jinja_env.from_string(template)
            for entry in input_json:
                if include_case_data:
                    entry.update({"SiemplifyEvents": events})
                    entry.update({"SiemplifyEntities": entities})
                result_value += template.render(entry, input_json=entry)
                output_message = "Successfully rendered the template."
        elif type(input_json) == dict:
            if include_case_data:
                input_json.update({"SiemplifyEvents": events})
                input_json.update({"SiemplifyEntities": entities})
                print(input_json)
            if jinja:
                template = jinja_env.from_string(jinja)
            else:
                template = jinja_env.from_string(template)
            result_value = template.render(input_json=input_json)
            output_message = "Successfully rendered the template."
        else:
            siemplify.LOGGER.error("Incorrect type.  Needs to be a list or dict.")

    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise  # used to return entire error details - including stacktrace back to client UI. Best for most usecases
        # in case you want to handle the error yourself, don't raise, and handle error result ouputs:
        status = EXECUTION_STATE_FAILED
        result_value = "Failed"
        output_message += "\n unknown failure"

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
