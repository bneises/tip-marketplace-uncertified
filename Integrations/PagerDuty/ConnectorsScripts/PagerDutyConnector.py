import sys
import uuid

from PagerDutyManager import PagerDutyManager
from SiemplifyConnectors import SiemplifyConnectorExecution
from SiemplifyConnectorsDataModel import AlertInfo
from SiemplifyUtils import (convert_string_to_unix_time, dict_to_flat,
                            output_handler)

CONNECTOR_NAME = "PagerDuty"
VENDOR = "PagerDuty"
PRODUCT = "PagerDuty"


@output_handler
def main(is_test_run):
    processed_alerts = []  # The main output of each connector run
    siemplify = SiemplifyConnectorExecution()  # Siemplify main SDK wrapper
    siemplify.script_name = CONNECTOR_NAME

    siemplify.LOGGER.info("------------------- Main - Started -------------------")

    if is_test_run:
        siemplify.LOGGER.info('***** This is an "IDE Play Button"\\"Run Connector once" test run ******')

    api_key = siemplify.extract_connector_param(param_name="apiKey")
    email = siemplify.extract_connector_param(param_name="email")
    timeframe = siemplify.extract_connector_param(param_name="timeframe")
    acknowledge_enabled = siemplify.extract_connector_param(param_name="acknowledge")

    manager = PagerDutyManager(api_key=api_key, email=email, timeframe=timeframe)
    try:
        incidents_list = manager.get_incidents()
        if incidents_list is None:
            siemplify.LOGGER.info("No events were retrieved for the specified timeframe from PagerDuty")
            return
        siemplify.LOGGER.info("Retrieved {} events from PagerDuty".format(len(incidents_list)))
        for incident in incidents_list:
            alert_id = incident["id"]

            # Map the severity in PagerDuty to the severity levels in Siemplify
            severity = get_siemplify_mapped_severity(incident["urgency"])

            siemplify_alert = build_alert_info(siemplify, incident, severity)
            
            if siemplify_alert:
                processed_alerts.append(siemplify_alert)
                siemplify.LOGGER.info("Added incident {} to package results".format(alert_id))
                # `acknowledge_enabled` is a str, hence the str comparison below
                if acknowledge_enabled == "true":
                    manager.acknowledge_incident(alert_id)
                    siemplify.LOGGER.info("Incident {} acknowledged in PagerDuty".format(alert_id))

    except Exception as e:
        siemplify.LOGGER.error("There was an error fetching or acknowledging incidents in PagerDuty")
        siemplify.LOGGER.exception(e)

    siemplify.LOGGER.info("------------------- Main - Finished -------------------")
    siemplify.return_package(processed_alerts)


def get_siemplify_mapped_severity(severity):
    severity_map = {"high": "100", "low": "-1"}
    return severity_map.get(severity)


def build_alert_info(siemplify, incident, severity):
    """Returns an alert, which is an aggregation of basic events."""

    alert_info = AlertInfo()
    alert_info.display_id = incident["id"]
    alert_info.ticket_id = str(uuid.uuid4())
    alert_info.name = "PagerDuty Incident: " + incident["title"]
    alert_info.rule_generator = incident["first_trigger_log_entry"]["summary"]
    alert_info.start_time = convert_string_to_unix_time(incident["created_at"])
    alert_info.severity = severity
    alert_info.device_vendor = VENDOR
    alert_info.device_product = PRODUCT
    alert_info.environment = siemplify.context.connector_info.environment
    alert_info.events.append(dict_to_flat(incident))

    return alert_info


if __name__ == "__main__":
    is_test_run = len(sys.argv) > 2 and sys.argv[1] == "True"
    main(is_test_run)
