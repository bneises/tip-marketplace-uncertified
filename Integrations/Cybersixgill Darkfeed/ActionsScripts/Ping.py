from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

from CybersixgillManager import SixgillEnrichManager,PROVIDER


@output_handler
def main():
    siemplify = SiemplifyAction()
    client_id = siemplify.extract_configuration_param(PROVIDER,"Client Id")
    client_secret = siemplify.extract_configuration_param(PROVIDER,"Client Secret")

    sixgill_manager = SixgillEnrichManager(client_id,client_secret)
    status,message,result = sixgill_manager.create_sixgill_client()
    siemplify.end(message, result, status)


if __name__ == "__main__":
    main()
