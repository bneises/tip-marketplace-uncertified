from datetime import datetime, timedelta

import requests


class PagerDutyManager(object):
    """Creates an object of PagerDutyManager

    Attributes:
        api_key: API Key needed to interact with PagerDuty API
        email: Email address associated with the API Key
        timeframe: Time range (in minutes) to retrieve events
    """

    BASE_URL = "https://api.pagerduty.com"
    INCIDENTS_URI = "/incidents"

    def __init__(self, api_key, email, timeframe):
        """Initializes PagerDutyManager with params as set in connector config"""
        self.api_key = api_key
        self.email = email
        self.timeframe = int(timeframe)

    def get_incidents(self):
        """
        Returns list of incidents triggered in PagerDuty
        API Reference: https://developer.pagerduty.com/api-reference/9d0b4b12e36f9-list-incidents
        """

        url = self.BASE_URL + self.INCIDENTS_URI
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": "Token token={}".format(self.api_key),
            "Content-Type": "application/json",
        }

        if self.timeframe == 0:
            params = {"date_range": "all", "statuses[]": "triggered"}
        else:
            since = datetime.utcnow() - timedelta(minutes=self.timeframe)
            params = {
                "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "until": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "statuses[]": "triggered",
            }

        resp = requests.get(url, headers=headers, params=params, timeout=5)

        resp.raise_for_status()
        return resp.json()["incidents"]

    def acknowledge_incident(self, incident_id):
        """
        Acknowledges an incident in PagerDuty
        API Reference: https://developer.pagerduty.com/api-reference/8a0e1aa2ec666-update-an-incident
        """
        url = self.BASE_URL + self.INCIDENTS_URI + "/{}".format(incident_id)
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": "Token token={}".format(self.api_key),
            "Content-Type": "application/json",
            "From": "{}".format(self.email),
        }

        data = {"incident": {"type": "incident_reference", "status": "acknowledged"}}

        resp = requests.put(url, json=data, headers=headers, timeout=5)
        if resp.ok:
            print("Incident acknowledged")
        else:
            print(resp.raise_for_status())
