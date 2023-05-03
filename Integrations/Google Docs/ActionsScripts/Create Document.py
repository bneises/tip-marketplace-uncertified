from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleDocsManager import GoogleDocsManager

IDENTIFIER = u'Google Docs'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    title = siemplify.extract_action_param(param_name=u'Title', is_mandatory=True)
    role = siemplify.extract_action_param(param_name=u'Role', is_mandatory=True)
    user_emails_to_add = siemplify.extract_action_param(param_name=u'Emails', is_mandatory=True)
    
    google_doc_manager = GoogleDocsManager(credentials_json)
    res = google_doc_manager.create_document(title,role,user_emails_to_add)
    
    siemplify.result.add_result_json(res)


    siemplify.end('Document created successfully', res['id'])


if __name__ == "__main__":
    main()
