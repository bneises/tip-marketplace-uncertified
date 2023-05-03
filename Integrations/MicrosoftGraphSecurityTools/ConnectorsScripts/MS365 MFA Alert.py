from SiemplifyConnectors import SiemplifyConnectorExecution
from SiemplifyConnectorsDataModel import AlertInfo
from SiemplifyUtils import output_handler, unix_now
from random import randrange
from MicrosoftGraphSecurityManager import MicrosoftGraphSecurityManager


import uuid
import sys
import json
import os

# ============================================================================#
# title           :MS365 NFA Alert
# description     :This connector monitors the MFA status of your userbase.
#                  If a discrepancy/MFA issue is found based on your given
#                  parameters, an alert will be generated.
# author          :Daniel Harvey
# date            :07-12-2020
# python_version  :3.7
# ============================================================================#

CONNECTOR_NAME = "MS365 MFA Alert"
VENDOR = "Microsoft"
PRODUCT = "Microsoft 365"
RULE_GENERATOR = "MFA"
RANDOM_ALERT_COUNT_MAX = 3
RANDOM_EVENT_COUNT_PER_ALERT_MAX = 5

@output_handler
def main(is_test_run):
    alerts = [] # The main output of each connector run
    siemplify = SiemplifyConnectorExecution() # Siemplify main SDK wrapper
    siemplify.script_name = CONNECTOR_NAME

    if (is_test_run):
        siemplify.LOGGER.info("***** This is an \"IDE Play Button\"\\\"Run Connector once\" test run ******")

    siemplify.LOGGER.info("==================== Main - Param Init ====================")

    client_id = siemplify.extract_connector_param(param_name="Client ID", print_value=True)
    secret_id = siemplify.extract_connector_param(param_name="Secret ID", print_value=False)
    tenant = siemplify.extract_connector_param(param_name="Tenant ID", print_value=False)
    certificate_password = siemplify.extract_connector_param(param_name="Certificate Password", print_value=False)
    certificate_path = siemplify.extract_connector_param(param_name="Certificate Path", print_value=True)
    filter_exclude_guests = siemplify.extract_connector_param(param_name="Exclude Guests", input_type=bool, print_value=False)
    alert_selfserv_reset = siemplify.extract_connector_param(param_name="Self Service Reset Alert", input_type=bool, print_value=False)
    alert_mfa_registration = siemplify.extract_connector_param(param_name="MFA Registration Alert", input_type=bool, print_value=False)
    account_whitelist = siemplify.whitelist

    siemplify.LOGGER.info("------------------- Main - Started -------------------")

    json_results = {}
    
    try:
        siemplify.LOGGER.info("Connecting to Microsoft Graph Security.")
        mtm = MicrosoftGraphSecurityManager(client_id, secret_id, certificate_path, certificate_password, tenant)
        siemplify.LOGGER.info("Connected successfully.")

        #siemplify.LOGGER.info(f"Fetching alert {alert_id}")
        mfa_stats = mtm.get_mfa_stats()

        if mfa_stats:
            siemplify.LOGGER.info(f"Found alert mfa stats.")
            for user in mfa_stats:
                alert_id = user['id']
                userPrincipalName = user['userPrincipalName']
                isMfaRegistered = user['isMfaRegistered']
                isCapable = user['isCapable']
                
                if filter_exclude_guests and "#EXT#" in userPrincipalName:
                    continue
                
                # Check MFA registration
                if (userPrincipalName not in account_whitelist and (not isMfaRegistered and alert_mfa_registration) or (isCapable and alert_selfserv_reset)):
                    try:
                        alert_example = fetch_alert(siemplify, alert_id, user)
                
                        if alert_example:
                            alerts.append(alert_example)
                            siemplify.LOGGER.info("Added Alert {} to package results".format(alert_id))
                
                    except Exception as e:
                        siemplify.LOGGER.error("Failed to process alert {}".format(alert_id), alert_id=alert_id)
                        siemplify.LOGGER.exception(e)

            json_results = json.dumps(mfa_stats)
            output_message = f'User MFA information was found.'
            result_value = json.dumps(mfa_stats)

        else:
            siemplify.LOGGER.info(f"No MFA information was found.")
            output_message = f"No MFA information was found."
            result_value = json.dumps({})


    except Exception as e:
        siemplify.LOGGER.error(f"Some errors occurred. Error: {e}")
        siemplify.LOGGER.exception(e)
        result_value = json.dumps({})
        output_message = f"Some errors occurred. Error: {e}"
        raise
    

    siemplify.LOGGER.info("------------------- Main - Finished -------------------")
    siemplify.return_package(alerts)


def fetch_alert(siemplify, alert_id, user):
    """Returns an alert, which is an aggregation of basic events. (ie: Arcsight's correlation, QRadar's Offense)"""
    siemplify.LOGGER.info("-------------- Started processing Alert {}".format(alert_id), alert_id=alert_id)

    alert_info = AlertInfo()

    alert_info.display_id = str(uuid.uuid4())
    alert_info.ticket_id = alert_id
    alert_info.name = "MFA Alert " + user['userPrincipalName']
    alert_info.rule_generator = RULE_GENERATOR
    alert_info.start_time = unix_now()
    alert_info.end_time = unix_now()
    alert_info.priority = 80  # Informative = -1,Low = 40,Medium = 60,High = 80,Critical = 100.
    alert_info.device_vendor = VENDOR  
    alert_info.device_product = PRODUCT
    # ----------------------------- Alert Fields initilization END -----------------------------

    siemplify.LOGGER.info("---------- Events fetching started for alert  {}".format(alert_id))

    event_id = str(uuid.uuid4())
    try:
        event = fetch_event(siemplify, alert_id, event_id, user)

        if event:
            alert_info.events.append(event)
            siemplify.LOGGER.info("Added Event {} to Alert {}".format(event_id, alert_id))

    except Exception as e:
        siemplify.LOGGER.error("Failed to process event {}".format(event_id), alert_id=alert_id)
        siemplify.LOGGER.exception(e)
        

    siemplify.LOGGER.info("---------- Events fetching finished for alert {}".format(alert_id))

    siemplify.LOGGER.info("-------------- Finished processing Alert {}".format(alert_id), alert_id=alert_id)
    return alert_info


def fetch_event(siemplify, alert_id, event_id, user):
    siemplify.LOGGER.info("--- Started processing Event:  alert_id: {} | event_id: {}".format(alert_id, event_id))
    event = {}

    event["StartTime"] = unix_now() 
    event["EndTime"] = unix_now() 
    event["name"] = "MFA problem detection"
    event["device_product"] = "Microsoft 365" 
    # ----------------------------- ---------------
    event["SourceUserName"] = user['userPrincipalName']
    event["userPrincipalName"] = user["userPrincipalName"]
    event["userDisplayName"] = user["userDisplayName"]
    event["isRegistered"] = user["isRegistered"]
    event["isCapable"] = user["isCapable"]
    event["isMfaRegistered"] = user["isMfaRegistered"]
    #event["authMethods"] = user["authMethods"]

    siemplify.LOGGER.info("--- Finished processing Event: alert_id: {} | event_id: {}".format(alert_id, event_id))

    return event

if __name__ == "__main__":
    # Connectors are run in iterations. The interval is configurable from the ConnectorsScreen UI.
    is_test_run = not (len(sys.argv) < 2 or sys.argv[1] == 'True')
    main(is_test_run)