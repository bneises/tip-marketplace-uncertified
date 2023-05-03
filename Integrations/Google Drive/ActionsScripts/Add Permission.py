from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleDriveManager import GoogleDriveManager

IDENTIFIER = u'Google Drive'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    file_id = siemplify.extract_action_param(param_name=u'File Id', is_mandatory=True)
    role = siemplify.extract_action_param(param_name=u'Role', is_mandatory=True)
    user_emails_to_add = siemplify.extract_action_param(param_name=u'Emails', is_mandatory=True)
    should_send_notification_str = siemplify.extract_action_param(param_name=u'Should send notification', is_mandatory=True)
    should_send_notification = bool(should_send_notification_str)

    google_drive_manager = GoogleDriveManager(credentials_json)

    emails = user_emails_to_add.split(";")
    for email in emails:
        google_drive_manager.insert_permission(file_id,role,email,should_send_notification)

    output_message = "Permission {0} for file <{1}> was granted to {2}.".format(role,file_id,user_emails_to_add)
    siemplify.end(output_message, file_id)


if __name__ == "__main__":
    main()
