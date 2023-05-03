from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
import requests

INTEGRATION_NAME = "Whois XML API"

SCRIPT_NAME = "Whois XML API Ping"

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    api_key = siemplify.extract_configuration_param(provider_name=INTEGRATION_NAME,
                                                    param_name="API Key")

    url = "https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={api_key}&domainName=google.com".format(api_key=api_key)

    res = requests.get(url)
    res.raise_for_status()

    if "ApiKey authenticate failed" in res.content.decode("utf-8"):
        raise Exception("Error, bad credentials")


    siemplify.end("Successful Connection", True)

if __name__ == "__main__":
    main()