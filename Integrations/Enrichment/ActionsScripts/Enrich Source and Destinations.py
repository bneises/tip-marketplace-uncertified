from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import json
import time
from datetime import datetime
import re

INVESTIGATOR_URL = '{}/external/v1/investigator/GetInvestigatorData/{}?format=camel'

ACTION_NAME = "Enrich Source and Destinations"


def get_alert_entities(siemplify):
    return [entity for alert in siemplify.case.alerts for entity in alert.entities if
            alert.identifier == siemplify.current_alert.identifier]


def get_ip_entities(siemplify):
    return [entity.identifier for entity in get_alert_entities(siemplify) if entity.entity_type == 'ADDRESS']


def get_host_entities(siemplify):
    return [entity.identifier for entity in get_alert_entities(siemplify) if entity.entity_type == 'HOSTNAME']


def get_current_alert(alerts, current_alert):
    for alert in alerts:
        if alert['identifier'] == current_alert:
            return alert


def get_sources_and_dest(alert):
    sources = []
    destinations = []
    for event_card in alert['securityEventCards']:
        sources.extend(event_card['sources'])
        destinations.extend(event_card['destinations'])

    if sources and isinstance(sources[0], dict):
        sources = [x["identifier"] for x in sources]
    if destinations and isinstance(destinations[0], dict):
        destinations = [x["identifier"] for x in destinations]
    return (sources, destinations)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME

    investigator_res = siemplify.session.get(INVESTIGATOR_URL.format(siemplify.API_ROOT, siemplify.case_id))
    investigator_res.raise_for_status()
    alert = get_current_alert(investigator_res.json()['alerts'], siemplify.current_alert.identifier)
    (sources, dests) = get_sources_and_dest(alert)
    updated_entities = []

    for source in sources:
        for entity in get_alert_entities(siemplify):
            if entity.identifier == source:
                entity.additional_properties.update({"isSource": "true"})
                updated_entities.append(entity)
                break
    for dest in dests:
        for entity in get_alert_entities(siemplify):
            if entity.identifier == dest:
                entity.additional_properties.update({"isDest": "true"})
                updated_entities.append(entity)
                break

    siemplify.update_entities(updated_entities)
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message : Enrichment added."  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.

    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()