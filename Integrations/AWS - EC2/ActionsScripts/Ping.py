from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from EC2Manager import EC2Manager

IDENTIFIER = u"AWS - EC2"

@output_handler
def main():
    siemplify = SiemplifyAction()

    access_key_id = siemplify.extract_configuration_param(IDENTIFIER,"Access Key ID")
    secret_access_key = siemplify.extract_configuration_param(IDENTIFIER, "Secret Access Key")
    default_region = siemplify.extract_configuration_param(IDENTIFIER, "Default Region")
    
    
    #Creating an instance of EC2Manager object
    ec2_manager = EC2Manager(access_key_id, secret_access_key, default_region)
    
    #Calling the function test_connectivity() from the EC2Manager
    response = ec2_manager.test_connectivity()

    if response:
        return_value = True
        output_message = 'Connected successfully'

    else:
        return_value = False
        output_message = 'The Connection failed'

    siemplify.end(output_message, return_value)


if __name__ == "__main__":
    main()
