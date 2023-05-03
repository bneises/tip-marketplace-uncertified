from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleDriveManager import GoogleDriveManager

IDENTIFIER = u'Google Drive'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    file_path = siemplify.extract_action_param(param_name=u'File Path', is_mandatory=True)
    share_to_emails = siemplify.extract_action_param(param_name=u'Share with emails')

    google_drive_manager = GoogleDriveManager(credentials_json)
    res = google_drive_manager.upload_file_from_path(file_path)
    file_id = res['id']
    if share_to_emails:
        emails = share_to_emails.split(";")
        for email in emails:
            google_drive_manager.insert_permission(file_id,'writer',email)

    siemplify.result.add_result_json(res)

    siemplify.end('File was uploaded to Google Drive successfully', res['id'], EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
