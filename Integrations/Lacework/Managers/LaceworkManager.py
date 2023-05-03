import requests
import constants
from datetime import datetime, timedelta, timezone

class LaceworkManager(object):
    """
    Lacework Manager
    """
    def __init__(self, key_id, secret, account_name):
        self.key_id = key_id
        self.secret = secret
        self.account_name = account_name
        self.base_url = "https://"+self.account_name

    def get_temp_token(self):
        url = self.base_url + constants.TEMP_TOKEN_URI
        headers, body = {}, {}
        headers["X-LW-UAKS"] = "{}".format(self.secret)
        headers["Content-Type"] = "application/json"
        body["keyId"] = self.key_id
        body["expiryTime"] = 3600

        # Make request
        resp = requests.post(url, headers=headers, json=body)

        #Extract and return temp token
        token = resp.json()["data"][0]["token"]
        return token

    def get_events_for_date_range(self, token):
        url = self.base_url + constants.EVENTS_FOR_DATE_RANGE_URI
        headers = {}
        headers["Authorization"] = "Bearer {}".format(token)

        # Calculate start and end time
        end_utc = datetime.now(timezone.utc)
        start_utc = end_utc - timedelta(hours=1)
        payload = {"START_TIME":"{}".format(start_utc.strftime('%Y-%m-%dT%H:%M:%SZ')), "END_TIME":"{}".format(end_utc.strftime('%Y-%m-%dT%H:%M:%SZ'))}

        # Make request
        resp = requests.get(url, params=payload, headers=headers)

        # Return list of events
        if resp.status_code == 200:
            events = resp.json()["data"]
            return events
        else:
            return None

    def get_event_details(self, event_id, token):
        url = self.base_url + constants.EVENT_DETAILS_BY_ID_URI
        headers = {}
        headers["Authorization"] = "Bearer {}".format(token)

        payload = {"EVENT_ID": "{}".format(event_id)}
        # Make request
        resp = requests.get(url, params=payload, headers=headers)

        # Return event details
        event_details = resp.json()["data"][0]
        return event_details