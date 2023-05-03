import traceback
import requests
import urllib3
import json

# Disable insecure warnings
urllib3.disable_warnings()


class ArcannaClient:
    """ Implements Arcanna API
    """

    def __init__(self, api_key, base_url, verify=True, proxy=False, default_job_id=-1):
        self.base_url = base_url
        self.verify = verify
        self.proxy = proxy
        self.api_key = api_key
        self.default_job_id = default_job_id

    def get_headers(self):
        """   Adds header

        """
        headers = {
            'accept': 'application/json',
            'x-arcanna-api-key': self.api_key
        }
        return headers

    def set_default_job_id(self, job_id):
        self.default_job_id = job_id

    def get_default_job_id(self):
        return self.default_job_id

    def test_arcanna(self):
        url_suffix = '/api/v1/health'
        raw_response = requests.get(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify, timeout=30)
        return raw_response.json()

    def list_jobs(self):
        url_suffix = '/api/v1/jobs'
        raw_response = requests.get(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify, timeout=30)
        if raw_response.status_code != 200:
            raise Exception(f"Error in API call [{raw_response.status_code}]. Reason: {raw_response.reason}")
        return raw_response.json()

    def send_raw_event(self, job_id, severity, title, raw_body):
        url_suffix = '/api/v1/events/'
        body = self.map_to_arcanna_raw_event(job_id, raw_body, severity, title)

        raw_response = requests.post(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify,
                                     json=body, timeout=30)
        if raw_response.status_code != 201:
            raise Exception(f"Error HttpCode={raw_response.status_code} text={raw_response.text}")
        return raw_response.json()

    def map_to_arcanna_raw_event(self, job_id, raw, severity, title):
        body = {
            "job_id": job_id,
            "title": title,
            "raw_body": raw
        }
        if severity is not None:
            body["severity"] = severity
        return body

    def get_event_status(self, job_id, event_id):
        url_suffix = f"/api/v1/events/{job_id}/{event_id}"
        raw_response = requests.get(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify, timeout=30)
        if raw_response.status_code != 200:
            raise Exception(f"Error HttpCode={raw_response.status_code}")
        return raw_response.json()

    def send_feedback(self, job_id, event_id, username, arcanna_label, closing_notes, indicators):
        url_suffix = f"/api/v1/events/{job_id}/{event_id}/feedback"
        body = self.map_to_arcanna_label(arcanna_label, closing_notes, username)
        if indicators:
            body["indicators"] = json.loads(indicators)
        raw_response = requests.put(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify,
                                    json=body, timeout=30)

        if raw_response.status_code != 200:
            raise Exception(f"Arcanna Error HttpCode={raw_response.status_code} body={raw_response.text}")
        return raw_response.json()

    @staticmethod
    def map_to_arcanna_label(arcanna_label, closing_notes, username):
        body = {
            "cortex_user": username,
            "feedback": arcanna_label,
            "closing_notes": closing_notes
        }
        return body

    def send_bulk(self, job_id, events):
        url_suffix = f"/api/v1/bulk/{job_id}"
        body = {
            "count": len(events),
            "events": events
        }
        raw_response = requests.post(url=self.base_url + url_suffix, headers=self.get_headers(), verify=self.verify,
                                     json=body, timeout=30)

        if raw_response.status_code != 201:
            raise Exception(f"Arcanna Error HttpCode={raw_response.status_code} body={raw_response.text}")
        return raw_response.json()
