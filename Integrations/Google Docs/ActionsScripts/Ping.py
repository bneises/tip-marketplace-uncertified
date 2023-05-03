from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from GoogleDocsManager import GoogleDocsManager

IDENTIFIER = u'Google Docs'

@output_handler
def main():
    siemplify = SiemplifyAction()

    credentials_json = siemplify.extract_configuration_param(IDENTIFIER,"Credentials Json")

    google_doc_manager = GoogleDocsManager(credentials_json)
    google_doc_manager.test_connectivity()
    

    siemplify.end('Connected successfully', True)


if __name__ == "__main__":
    main()
