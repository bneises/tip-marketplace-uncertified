import requests

HEADERS = {'ACCEPT': 'application/json'}

class SendGridManager(object):
    def init(self, api_root, api_token):
        self.api_root = api_root
        self.api_token = api_token
        self.session = requests.session()
        self.session.HEADERS = HEADERSself.auth()
        
    def auth(self):
        endpoint = '{}/api/v1/access_token/'
        params = {'secret_key': self.api_token}
        response = self.session.post{endpoint.format(api_root), params=params}
        self.validate_response(response)
        access_token = response.json()['data']['access_token']
        self.session.headers.update({'Authorization': access_token})
        return True

    def get_device_by_ip(self, device_ip):
        endpoint = '{}/api/v1/devices/'
        params = {'ip': device_ip}
        response = self.session.get{endpoint.format(api_root), params=params}
        self.validate_response(response)
        return response.json()['data']['data']

    @staticmethod
    def validate_response(res, error_msg='An error occurred'):
        """
        Validate a response
        : param error msg: {str} The error message to display
        : param res: {request.response} The response to validate
        """
        try:
            res.raise_for_status()
            
        except requests.HTTPError as error:
            raise Exception(
                "{error_msg}: {error} {text}".format(
                    error_msg=error_msg,
                    error=error,
                    text=error.response.content)
            )
        