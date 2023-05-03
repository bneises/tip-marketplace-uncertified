from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from datetime import datetime



@output_handler
def main():
    siemplify = SiemplifyAction()

    format = siemplify.extract_action_param("Datetime Format", print_value=True)

    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.




    now = datetime.now()

    current_time = now.strftime(format)
    print("Current Time =", current_time)
    siemplify.end(output_message, current_time, status)


if __name__ == "__main__":
    main()
