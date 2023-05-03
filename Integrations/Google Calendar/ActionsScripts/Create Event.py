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

    event_json_str = siemplify.extract_action_param(param_name=u'Event Json', is_mandatory=True)
    behalf_email = siemplify.extract_action_param(param_name=u'Organizer', is_mandatory=True)

    event_json = json.loads(event_json_str)
    google_calendar_manager = GoogleCalendarManager(credentials_json,behalf_email)
    event_details = google_calendar_manager.create_event(event_json)
    
    res_json = json.dumps(event_details)
    siemplify.result.add_result_json(res_json)


    siemplify.end('Event created successfully in Google Calendar', True)


if __name__ == "__main__":
    main()
