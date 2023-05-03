from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

GLOBAL_CONTEXT = 0
IDENTIFIER = "GLOBAL"


def get_global_context(smp, key):
    """
    Get a global context property.

    :param smp: The SMP object.
    :param key: The key of the property to get.
    :return: The value of the property.
    """
    return smp.get_context_property(GLOBAL_CONTEXT, IDENTIFIER, key)

def set_global_context(smp, key, value):
    """
    Sets a global context property.

    :param smp: The SMP object.
    :param key: The key of the property.
    :param value: The value of the property.
    """
    smp.set_context_property(GLOBAL_CONTEXT, IDENTIFIER, key, value)

@output_handler
def main():
    siemplify = SiemplifyAction()
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    
    scope = siemplify.extract_action_param(param_name="Scope", is_mandatory=True, print_value=True, default_value='Alert')
    key = siemplify.extract_action_param(param_name="Key", is_mandatory=True, print_value=True)
    value = siemplify.extract_action_param(param_name="Value", is_mandatory=True, print_value=True)
    delim = siemplify.extract_action_param(param_name="Delimiter", is_mandatory=True, print_value=True, default_value=',')
    
    result_value = None
    try:
        
        if scope == 'Alert':
            result_value = siemplify.get_alert_context_property(key)
            if result_value:
                siemplify.set_alert_context_property(key, result_value+delim+value)
                result_value = result_value+delim+value
            else:
                siemplify.set_alert_context_property(key, value)
                result_value = value
        
        elif scope == 'Case':
            result_value = siemplify.get_case_context_property(key)
            if result_value:
                result_value = result_value+delim+value
                siemplify.set_case_context_property(key, result_value+delim+value)
            else:
                siemplify.set_case_context_property(key, value)
                result_value = value

        elif scope == "Global":
            result_value = get_global_context(siemplify, key)
            if result_value:
                
                set_global_context(siemplify, key, result_value+delim+value)
                result_value = result_value+delim+value
            else:
                set_global_context(siemplify, key, value)
                result_value = value
        if result_value:
            result_value = result_value.strip('"')
            output_message = "Successfully appended field {0} with value '{1}' in scope {2}.".format(key,value,scope)
        else:
            output_message = "Key: {0} in scope {1} didn't exist, it's now created".format(key, scope)
    except Exception as e:
        output_message = f"Error: {e}"
        status = EXECUTION_STATE_FAILED
        result_value = False
       

    siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)

if __name__ == "__main__":
    main()
