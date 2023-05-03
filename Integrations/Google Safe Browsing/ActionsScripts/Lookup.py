from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from pysafebrowsing import SafeBrowsing

IDENTIFIER = u'Google Safe Browsing'

@output_handler
def main():
    siemplify = SiemplifyAction()

    api_key = siemplify.extract_configuration_param(IDENTIFIER,"Api Key")
    url = siemplify.extract_action_param(param_name=u'Url', is_mandatory=True)

    safe_browsing_manager = SafeBrowsing(api_key)
    res = safe_browsing_manager = safe_browsing_manager.lookup_urls([url])
    is_malicious_str = res[url]['malicious']
    siemplify.result.add_result_json(res)

    is_malicious_bool = bool(is_malicious_str)
    
    if is_malicious_bool:
        siemplify.end('The URL was found malicious', is_malicious_bool)
    else:
        siemplify.end('The URL was not found malicious', is_malicious_bool)


if __name__ == "__main__":
    main()
