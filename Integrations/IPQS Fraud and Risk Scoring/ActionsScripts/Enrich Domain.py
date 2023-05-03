from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from IPQSManager import IPQSManager, PROVIDER
from SiemplifyDataModel import EntityTypes


@output_handler
def main():
    siemplify = SiemplifyAction()
    data_json = {}
    api_key = siemplify.extract_configuration_param(PROVIDER,"API Key")
    strictness = int(siemplify.extract_action_param(param_name="Strictness", print_value=True))
    fast = siemplify.extract_action_param(param_name="Fast", print_value=True)
    data_json['strictness'] = strictness
    if fast:
        data_json['fast'] = 'true'
    ipqs_manager = IPQSManager(siemplify, api_key, data_json)
    ipqs_manager.enrich([EntityTypes.HOSTNAME])

if __name__ == "__main__":
    main()
