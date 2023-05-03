from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT


ALERT_SCORE = 'ALERT_SCORE'
@output_handler
def main():
    siemplify = SiemplifyAction()

    _input = siemplify.extract_action_param("Input")
    current_score = siemplify.get_alert_context_property(ALERT_SCORE)
    if current_score is not None:
        current_score = current_score.strip('"')
    else:
        current_score = 0

    new_score = str(int(current_score) + int(_input))
    updated_score = siemplify.set_alert_context_property(ALERT_SCORE,new_score)
    
    result_value = new_score
    output_message = f"The Alert Score has been updated to: {new_score}"

    siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)

if __name__ == "__main__":
    main()
