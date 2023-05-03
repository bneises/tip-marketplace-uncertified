from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleCalendarManager import GoogleCalendarManager

IDENTIFIER = u'Google Calendar'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    google_calendar_manager = GoogleCalendarManager(credentials_json)
    google_calendar_manager.test_connectivity()
    

    siemplify.end('Connected successfully', True)


if __name__ == "__main__":
    main()
