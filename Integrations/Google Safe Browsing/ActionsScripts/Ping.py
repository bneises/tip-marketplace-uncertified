from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from pysafebrowsing import SafeBrowsing

IDENTIFIER = u'Google Safe Browsing'

@output_handler
def main():
    siemplify = SiemplifyAction()

    api_key = siemplify.extract_configuration_param(IDENTIFIER,"Api Key")
    
    safe_browsing_manager = SafeBrowsing(api_key)
    safe_browsing_manager = safe_browsing_manager.lookup_urls(['http://malware.testing.google.test/testing/malware/'])


    siemplify.end('Connected successfully', True)


if __name__ == "__main__":
    main()
