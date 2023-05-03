from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json
import time
from datetime import datetime

GET_INTEGRATIONS = '{}/external/v1/integrations/GetEnvironmentInstalledIntegrations'

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "GetIntegrationInstances"
    
    env_search = [siemplify._environment, "*"]
    json_payload = {"name": "*" }
    instances = []
    for env in env_search:
        json_payload = {"name": env }
        siemplify_integrations = siemplify.session.post(GET_INTEGRATIONS.format(siemplify.API_ROOT), json=json_payload)
        siemplify_integrations.raise_for_status()
        instances.extend(siemplify_integrations.json()['instances'])
    
    siemplify.result.add_result_json({"instances": instances})
    output_message = "Returned Instances."
    siemplify.end(output_message, True)

if __name__ == "__main__":
    main()