from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

GLOBAL_CONTEXT = 0
IDENTIFIER = "GLOBAL"


def get_global_context(smp, key):
    return smp.get_context_property(GLOBAL_CONTEXT, IDENTIFIER, key)


@output_handler
def main():
    siemplify = SiemplifyAction()

    scope = siemplify.extract_action_param("Scope")
    key = siemplify.extract_action_param("Key")

    result_value = None

    if scope == 'Alert':
        result_value = siemplify.get_alert_context_property(key)

    elif scope == 'Case':
        result_value = siemplify.get_case_context_property(key)

    elif scope == "Global":
        result_value = get_global_context(siemplify, key)

    output_message = "Not found value for key: {0} in scope {1}".format(key, scope)

    if result_value:
        result_value = result_value.strip('"')
        output_message = "Successfully found '{0}' for key: {1} in scope {2}.".format(result_value, key, scope)

    siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)

if __name__ == "__main__":
    main()
