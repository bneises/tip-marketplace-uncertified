from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from jinja2 import Template, Environment
from inspect import getmembers, isfunction
import json
import dateutil
import time
import JinjaFilters
import copy

# Example Consts:
INTEGRATION_NAME = "TemplateEngine"
SCRIPT_NAME = "Entity Insight"


@output_handler
def filter_datetime(date, fmt=None):
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format = "%Y/%m/%d %H:%M:%S"
    return native.strftime(format)


def map_priority(p):
    PRIORITY = {
        '-1': 'info',
        '40': 'low',
        '60': 'medium',
        '80': 'high',
        '100': 'critical'
    }
    return PRIORITY.get(p)


def timectime(s):
    return time.ctime(s)  # datetime.datetime.fromtimestamp(s)


def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info("================= Main - Param Init =================")
    # INIT ACTION PARAMETERS:
    json_object = siemplify.extract_action_param(param_name="JSON Object", is_mandatory=True, print_value=False)
    template = siemplify.extract_action_param(param_name="Template", is_mandatory=True, print_value=False)
    IDENTIFIER = siemplify.extract_action_param(param_name="Triggered By", is_mandatory=True, print_value=False)

    remove_br = str(siemplify.extract_action_param(param_name="Remove BRs",
                                                   is_mandatory=False,
                                                   print_value=False,
                                                   default_value='false')).lower() == 'true'
    create_insight = str(siemplify.extract_action_param(param_name="Create Insight",
                                                        is_mandatory=False,
                                                        print_value=False,
                                                        default_value='true')).lower() == 'true'

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    entities = {}
    json_result = {}
    for entity in siemplify.target_entities:
        if entity.additional_properties["Type"] != "ALERT":
            entities[entity.additional_properties["Identifier"]] = entity.additional_properties

    try:
        status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
        output_message = "output message :"  # human readable message, showed in UI as the action result
        result_value = None  # Set a simple result value, used for playbook if\else and placeholders.

        if siemplify.target_entities:
            try:
                input_json = json.loads(json_object)
            except Exception as e:
                siemplify.LOGGER.error("Error parsing JSON Object: {}".format(json_object))
                siemplify.LOGGER.exception(e)
                raise
                status = EXECUTION_STATE_FAILED
                result_value = "Failed"
                output_message += "\n failure parsing JSON object."
            jinja_env = Environment(autoescape=True)
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
            

            if remove_br:
                template = template.replace("<br>", "")
            pre_temp = template
            template = jinja_env.from_string(template)
            for entity in siemplify.target_entities:
                siemplify.LOGGER.info("Started processing entity: {}".format(entity.identifier))
                result_value = ''
                for entry in input_json:
                    if entry['Entity'].lower() == entity.identifier.lower():
                        update_json = {}
                        try:
                            update_json = entry['EntityResult'].copy()
                        except:
                            pass
                        if isinstance(update_json, dict):
                            update_json['entity'] = entities[entity.identifier].copy()
                        elif isinstance(update_json, list):
                            update_json = {
                                "entity": entities[entity.identifier].copy(),
                                "results": entry['EntityResult'].copy()
                            }
                        else:
                            raise Exception(f"Unsupported Entity Results type: {type(update_json)}")
                        result_value += template.render(update_json)
                        _res = {'entity_insight': result_value, 'template': pre_temp}
                        json_result[entity.identifier] = _res
                        siemplify.result.add_entity_json(entity.identifier, _res)
                        if create_insight and result_value != '':
                            siemplify.LOGGER.info("Creating Insight for entity: {}".format(entity.identifier))
                            siemplify.add_entity_insight(entity, result_value, triggered_by=IDENTIFIER)
                        output_message = "Successfully rendered the template."
    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise  # used to return entire error details - including stacktrace back to client UI. Best for most usecases
        # in case you want to handle the error yourself, don't raise, and handle error result ouputs:
        status = EXECUTION_STATE_FAILED
        result_value = "Failed"
        output_message += "\n unknown failure"
    siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_result))
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, '', status)


if __name__ == "__main__":
    main()
