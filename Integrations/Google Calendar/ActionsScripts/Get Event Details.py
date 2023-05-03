from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleCalendarManager import GoogleCalendarManager
import json
IDENTIFIER = u'Google Calendar'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    behalf_email = siemplify.extract_action_param(param_name=u'Organizer', is_mandatory=True)
    event_id = siemplify.extract_action_param(param_name=u'Event Id', is_mandatory=True)



    google_calendar_manager = GoogleCalendarManager(credentials_json,behalf_email)
    event_details = google_calendar_manager.get_event_details(event_id)

    output_message = ""
    ret_val = False
    
    if event_details != None:
        res_json = json.dumps(event_details)
        siemplify.result.add_result_json(res_json)
        ret_val = True
        output_message = "Found Calendar event with id <{0}>.".format(event_id)
    else:
        ret_val = False
        output_message = "Couldn't find Calendar event with id <{0}>.".format(event_id)

    siemplify.end(output_message, ret_val)


if __name__ == "__main__":
    main()
