from sixgill.sixgill_base_client import SixgillBaseClient
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT

PROVIDER = "Cybersixgill"
SIXGILL_CHANNEL_ID = "1f4fdd520d3a721799fc0d044283d364"

class SixgillManagerError(Exception):
    """
    Exception for Sixgill Manager
    """
    pass

class SixgillEnrichManager(object):
    def __init__(self,client_id,client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def create_sixgill_client(self):
        sixgill_darkfeed_client = None 
        try:
            sixgill_darkfeed_client = SixgillBaseClient(self.client_id, self.client_secret, SIXGILL_CHANNEL_ID)
            sixgill_access_token = sixgill_darkfeed_client.get_access_token()
            if sixgill_access_token:
                status = EXECUTION_STATE_COMPLETED
                msg = "Successfully Connected to Sixgill"
                result = True
        except Exception as err:
            raise SixgillManagerError(f"create_sixgill_client Error - {err}")
        return status, msg, result
