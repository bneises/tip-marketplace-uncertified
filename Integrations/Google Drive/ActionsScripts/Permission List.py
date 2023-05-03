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

    google_drive_manager = GoogleDriveManager(credentials_json)
    res = google_drive_manager.list_permissions(file_id)

    perms_count = len(res)
    siemplify.result.add_result_json(res)

    output_message = "{0} permissions were found for file <{1}>.".format(perms_count, file_id)
    siemplify.end(output_message, perms_count)


if __name__ == "__main__":
    main()
