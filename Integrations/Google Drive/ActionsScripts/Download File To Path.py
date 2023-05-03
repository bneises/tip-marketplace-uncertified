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
    folder_to_save = siemplify.extract_action_param(param_name=u'Folder Path',is_mandatory=True)


    
    google_drive_manager = GoogleDriveManager(credentials_json)
    res = google_drive_manager.download_file_to_path(file_id,folder_to_save)
    
    siemplify.result.add_result_json(res)

    output_message = "File <{0}:{1}> was successfully downloaded to path {2}.".format(res['name'],file_id, res['saved_to'])
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()
