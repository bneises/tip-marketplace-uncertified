from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes

from SixgillManager import SixgillEnrichManager,PROVIDER
from SixgillResultProcessor import SixgillActionResultProcessor

@output_handler
def main():
    siemplify = SiemplifyAction()
    client_id = siemplify.extract_configuration_param(PROVIDER,"Client Id")
    client_secret = siemplify.extract_configuration_param(PROVIDER,"Client Secret")

    sixgill_manager = SixgillEnrichManager(client_id,client_secret)
    sixgill_process = SixgillActionResultProcessor(siemplify,sixgill_manager)
    sixgill_process.entity_data([EntityTypes.HOSTNAME])
    sixgill_process.enrich([EntityTypes.HOSTNAME])
    

if __name__ == "__main__":
    main()



