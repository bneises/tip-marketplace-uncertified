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
    permission_id = siemplify.extract_action_param(param_name=u'Permission Id', is_mandatory=True)

    google_drive_manager = GoogleDriveManager(credentials_json)
    google_drive_manager.remove_permission(file_id,permission_id)

    output_message = "Permission <{0}> for file <{1}> was successfully removed.".format(permission_id, file_id)
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()
