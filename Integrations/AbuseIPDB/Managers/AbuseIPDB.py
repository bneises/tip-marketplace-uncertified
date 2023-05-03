# =====================================
#              IMPORTS                #
# =====================================
import requests
from datamodels import IP
import os
from datetime import datetime

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# title          :AbuseIPDB.py
# description    :This Module contains all current AbuseIPDB functionality
# author         :Daniel Harvey
# date           :7-DEC-2020
# python_version :3.7
# Doc            :https://www.abuseipdb.com/api
# ==============================================================================

# =====================================
#             CONSTANTS               #
# =====================================
URL_TYPE = u'url'
DUMMY_IP_FOR_TEST = u'40.76.4.15'

API_ROOT = u'https://api.abuseipdb.com/api/v2/{0}'

# Scan IP messages indicators.
NO_DATA_FOUND_MESSAGE = u'No Data Found'
RESOURCE_COULD_NOT_BE_FOUND_MESSAGE = u'resource could not be found'
INVALID_MESSAGE = u'Invalid'
TIME_FORMAT = u"%Y-%m-%d %H:%M:%S"


# =====================================
#              CLASSES                #
# =====================================
class AbuseIPDBManagerError(Exception):
    """
    General Exception for AbuseIPDB manager
    """
    pass


class AbuseIPDBLimitManagerError(Exception):
    """
    Limit Reached for AbuseIPDB manager
    """
    pass


class AbuseIPDBInvalidAPIKeyManagerError(Exception):
    """
    Invalid API key exception for AbuseIPDB manager
    """
    pass


class AbuseIPDBManager(object):
    def __init__(self, api_key, verify_ssl=True):
        self.api_key = api_key

    #
    def validate_response(self, response, error_msg=u"An error occurred"):
        """
        Retrieve a report on a given url/file
        :param response: {dict} response from api call,
        :param error_msg: {string} message if response is not valid
        :return: {bool}
        """
        try:
            response.raise_for_status()

            if response.status_code == 204:
                # API limit reached
                raise AbuseIPDBLimitManagerError(u"Request rate limit exceeded")

        except requests.HTTPError as error:
            if response.status_code == 403:
                # Forbidden - no permission to resource.
                # You don't have enough privileges to make the request. You may be doing a request without providing
                # an API key or you may be making a request to a Private API without having the appropriate privileges.
                raise AbuseIPDBInvalidAPIKeyManagerError(
                    u"Forbidden. You don't have enough privileges to make the request. You may be doing a request "
                    u"without providing an API key or you may be making a request to a Private API without having "
                    u"the appropriate privileges"
                )

            # Not a JSON - return content
            raise AbuseIPDBManagerError(
                u"{error_msg}: {error} - {text}".format(
                    error_msg=error_msg,
                    error=error,
                    text=error.response.content)
            )

        return True

    def validate_max_days(self, max_days):
        if str(max_days).isdigit():
            return int(max_days)
        else:
            raise AbuseIPDBInvalidAPIKeyManagerError(
                u"Failed to parse parameter. Please give a valid integer for the parameter\"Max Age in Days\""
            )

    def test_connectivity(self):
        """
        Ping to server to be sure that connected
        :return: {bool}
        """
        max_days = 90
        return True if self.check_ip(DUMMY_IP_FOR_TEST, max_days) else False

    def check_ip(self, resource, max_days):
        """
        Retrieve a report on a given IP
        :param resource: {string} The IP,
        :return: {dict}
        """
        params = {
            u'ipAddress': resource,
            u'maxAgeInDays': str(max_days)
        }
        headers = {
            'Accept': 'application/json',
            'Key': self.api_key
        }
        check_url = API_ROOT.format(u'check')
        response = requests.request(method='GET', url=check_url, headers=headers, params=params)
        self.validate_response(response)

        json_object = response.json().get(u'data')

        return self.build_ip_address_object(json_object)

    def build_ip_address_object(self, json_object):
        return IP(
            raw_data=json_object,
            isPublic=json_object.get(u'isPublic'),
            ipVersion=json_object.get(u'ipVersion'),
            isWhitelisted=json_object.get(u'isWhitelisted'),
            abuseConfidenceScore=json_object.get(u'abuseConfidenceScore'),
            countryCode=json_object.get(u'countryCode'),
            countryName=json_object.get(u'countryName'),
            usageType=json_object.get(u'usageType'),
            isp=json_object.get(u'isp'),
            domain=json_object.get(u'domain'),
            hostnames=json_object.get(u'hostnames'),
            totalReports=json_object.get(u'totalReports'),
            numDistinctUsers=json_object.get(u'numDistinctUsers'),
            lastReportedAt=json_object.get(u'lastReportedAt'),
            reports=json_object.get(u'reports')
        )

