from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT

GLOBAL_CONTEXT = 0
IDENTIFIER = "GLOBAL"

def set_global_context(smp, key, value):
    smp.set_context_property(GLOBAL_CONTEXT, IDENTIFIER, key, value)

@output_handler
def main():
    siemplify = SiemplifyAction()

    scope = siemplify.extract_action_param("Scope")
    key = siemplify.extract_action_param("Key")
    value = siemplify.extract_action_param("Value")

    if scope == 'Alert':
        siemplify.set_alert_context_property(key,value)
    elif scope == 'Case':
        siemplify.set_case_context_property(key,value)
    elif scope == "Global":
        set_global_context(siemplify, key, value)

    output_message = "Successfully Updated field {0} with value '{1}' in scope {2}.".format(key,value,scope)

    siemplify.end(output_message, True, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
