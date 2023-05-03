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
    country = siemplify.extract_action_param(param_name="Country", print_value=True)
    data_json['strictness'] = strictness
    if country:
        data_json['country'] = country
    ipqs_manager = IPQSManager(siemplify, api_key, data_json)
    ipqs_manager.enrich([EntityTypes.PHONENUMBER])

if __name__ == "__main__":
    main()
