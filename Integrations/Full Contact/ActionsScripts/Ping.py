import requests

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from SiemplifyDataModel import EntityTypes



class FullContactManager(object):
    def __init__(self, api_key):
        # self.api_key = api_key
        self._headers = {'Authorization': 'Bearer {}'.format(api_key)}

    def enrich_person(self, email):
        url = 'https://api.fullcontact.com/v3/person.enrich'
        data = {'email': email}
        res = requests.post(url, headers=self._headers, json=data, verify=False)
        return res

    def enrich_domain(self, domain):
        url = 'https://api.fullcontact.com/v3/company.enrich'
        data = {'domain': domain}
        res = requests.post(url, headers=self._headers, json=data, verify=False)
        return res


@output_handler
def main():
    siemplify = SiemplifyAction()

    domain = "google.com"
    api_key = siemplify.get_configuration("Full Contact")["API Key"]

    if domain:
        fcm = FullContactManager(api_key)
        res2 = fcm.enrich_domain(domain).json()
        if "status" in res2 and res2["status"] == 401:
            raise Exception(res2)

    output_message = 'Success'
    result_value = True

    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
