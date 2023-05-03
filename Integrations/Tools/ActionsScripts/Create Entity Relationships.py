from SiemplifyUtils import output_handler, add_prefix_to_dict, dict_to_flat, convert_dict_to_json_result_dict
from SiemplifyAction import SiemplifyAction
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import requests
import json
import time
from datetime import datetime
import re

EXTEND_GRAPH_URL = '{}/external/v1/investigator/ExtendCaseGraph'
ACTION_NAME = "Create Entity Relationships"


def get_alert_entities(siemplify):
    alert_entities = []
    for alert in siemplify.case.alerts:
        for entity in alert.entities:
            if entity.alert_identifier == siemplify.current_alert.identifier:
                alert_entities.append(entity)
    return alert_entities


def create_entity_relationship_by_type(siemplify, new_entity, entity_type, json_payload):
    payload = json_payload.copy()
    payload["typesToConnect"].append(entity_type)
    payload["entityIdentifier"] = new_entity
    created_entity = siemplify.session.post(EXTEND_GRAPH_URL.format(siemplify.API_ROOT), json=payload)
    created_entity.raise_for_status()


def create_entity_relationship_by_entity(siemplify, new_entity, linked_entity, json_payload):
    payload = json_payload.copy()
    payload["entityToConnectRegEx"] = "{}$".format(re.escape(linked_entity))
    payload["entityIdentifier"] = new_entity
    created_entity = siemplify.session.post(EXTEND_GRAPH_URL.format(siemplify.API_ROOT), json=payload)
    created_entity.raise_for_status()


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    output_message = "No Entity was created"
    result_value = "False"
    status = EXECUTION_STATE_COMPLETED
    separator = siemplify.extract_action_param("Separator Character", ",")
    entity_identifiers = list(
        filter(None, [x.strip() for x in siemplify.extract_action_param("Entity Identifier(s)", " ").split(separator)]))
    linked_entities = list(filter(None, [x.strip() for x in
                                         siemplify.extract_action_param("Target Entity Identifier(s)", " ").split(
                                             separator)]))
    linked_entity_type = siemplify.extract_action_param("Target Entity Type", None)

    entity_type = siemplify.extract_action_param('Entity Identifier(s) Type')
    is_relation_type = False
    is_source = False
    rel_direction = siemplify.extract_action_param('Connect As')

    json_data = siemplify.parameters.get("Enrichment JSON", None)
    if json_data == '// Enter some code here':
        json_data = None
    enrichment_json = {}

    if json_data:
        enrichment_json = json.loads(json_data)

    if rel_direction == "Source":
        is_source = True
        is_relation_type = True

    if rel_direction == "Destination":
        is_source = False
        is_relation_type = True

    if rel_direction == "Linked":
        is_relation_type = False

    enrich_dict = {}
    updated_entities = []

    json_results = {}
    entities_to_enrich = []
    case_id = siemplify.case_id
    alert_identifier = siemplify.current_alert.identifier
    output_message = ""

    json_payload = {
        "caseId": case_id,
        "alertIdentifier": alert_identifier,
        "entityType": entity_type,
        "isPrimaryLink": is_relation_type,
        "isDirectional": is_source,
        "typesToConnect": []
    }

    target_entities = []

    for entity in entity_identifiers:
        json_results[entity] = {}

    enrichment_entities = {}
    siemplify.LOGGER.info("Entities to create:{}".format(entity_identifiers))
    alert_entities = get_alert_entities(siemplify)

    for entity in alert_entities:
        if len(linked_entities) > 0:
            for l_entity in linked_entities:
                if entity.entity_type == linked_entity_type and entity.identifier == l_entity:
                    target_entities.append(entity.identifier)
        else:
            if entity.entity_type == linked_entity_type:
                target_entities.append(entity.identifier)

    siemplify.LOGGER.info("Possible Relationship entities:{}".format(target_entities))

    if len(target_entities) == 0:
        output_message = "No entity relationships found. Did not create entity."

    if len(target_entities) == len(entity_identifiers) and len(linked_entities) > 0:

        for linked_entity, new_entity_identifier in zip(target_entities, entity_identifiers):
            linked_entities_arr = []
            try:
                create_entity_relationship_by_entity(siemplify, new_entity_identifier, linked_entity, json_payload)
                result_value = True
                linked_entities_arr.append(linked_entity)
                output_message += f"The Entity {new_entity_identifier} was created and linked to {linked_entity} : {linked_entity_type} successfully\n"
            except Exception as e:
                siemplify.LOGGER.error("Error creating entity:{}, error: {}".format(linked_entity, e))
                status = EXECUTION_STATE_FAILED

            siemplify.LOGGER.info(
                f"The Entity {new_entity_identifier} was created and linked to {linked_entity} : {linked_entity_type} successfully\n")

            json_results[new_entity_identifier]['status'] = 'created'
            linked_entity_obj = {}
            linked_entity_obj['entity_type'] = linked_entity_type
            linked_entity_obj['entities'] = linked_entities_arr

            json_results[new_entity_identifier]['linked_entities'] = linked_entity_obj
            json_results[new_entity_identifier]['entity_type'] = entity_type

    elif len(target_entities) > len(entity_identifiers) and len(entity_identifiers) == 1 and len(linked_entities) > 0:
        linked_entities_arr = []
        for target_entity in target_entities:
            try:
                create_entity_relationship_by_entity(siemplify, entity_identifiers[0], target_entity, json_payload)
                result_value = True
                linked_entities_arr.append(target_entity)
            except Exception as e:
                siemplify.LOGGER.error("Error creating entity:{}, error: {}".format(target_entity, e))
                status = EXECUTION_STATE_FAILED
            output_message += f"The Entity {entity_identifiers[0]} was created and linked to {target_entity} : {linked_entity_type} successfully\n"

            siemplify.LOGGER.info(
                f"The Entity {entity_identifiers[0]} was created and linked to {target_entity} : {linked_entity_type} successfully\n")

        json_results[entity_identifiers[0]]['status'] = 'created'
        linked_entity_obj = {}
        linked_entity_obj['entity_type'] = linked_entity_type
        linked_entity_obj['entities'] = linked_entities_arr
        json_results[entity_identifiers[0]]['linked_entities'] = linked_entity_obj


    elif len(entity_identifiers) > len(target_entities) and len(target_entities) == 1 and len(linked_entities) > 0:

        for new_entity_identifier in entity_identifiers:
            linked_entities_arr = []
            linked_entity = target_entities[0]
            try:
                create_entity_relationship_by_entity(siemplify, new_entity_identifier, linked_entity, json_payload)
                result_value = True
                linked_entities_arr.append(linked_entity)
            except Exception as e:
                siemplify.LOGGER.error("Error creating entity:{}, error: {}".format(linked_entity, e))
                status = EXECUTION_STATE_FAILED
            output_message += f"The Entity {new_entity_identifier} was created and linked to {linked_entity} : {linked_entity_type} successfully\n"

            siemplify.LOGGER.info(
                f"The Entity {new_entity_identifier} was created and linked to {linked_entity} : {linked_entity_type} successfully\n")

            json_results[new_entity_identifier]['status'] = 'created'
            linked_entity_obj = {}
            linked_entity_obj['entity_type'] = linked_entity_type
            linked_entity_obj['entities'] = linked_entities_arr
            json_results[new_entity_identifier]['linked_entities'] = linked_entity_obj
            json_results[new_entity_identifier]['entity_type'] = entity_type

    elif not linked_entities and target_entities != 0:
        linked_entities_arr = target_entities
        for new_entity_identifier in entity_identifiers:
            try:
                create_entity_relationship_by_type(siemplify, new_entity_identifier, linked_entity_type, json_payload)
            except Exception as e:
                siemplify.LOGGER.error("Error creating entity:{}, error: {}".format(new_entity_identifier, e))
                status = EXECUTION_STATE_FAILED
            result_value = True
            target_entities_str = ",".join(target_entities)
            siemplify.LOGGER.info(
                f"The Entity {new_entity_identifier} was created and linked to {target_entities_str} successfully\n")
            output_message += f"The Entity {new_entity_identifier} was created and linked to {target_entities_str} successfully\n"
            json_results[new_entity_identifier]['status'] = 'created'

            linked_entity_obj = {}
            linked_entity_obj['entity_type'] = linked_entity_type
            linked_entity_obj['entities'] = linked_entities_arr
            json_results[new_entity_identifier]['linked_entities'] = linked_entity_obj
            json_results[new_entity_identifier]['entity_type'] = entity_type

    time.sleep(3)
    siemplify.load_case_data()
    if enrichment_json:
        alert_entities = get_alert_entities(siemplify)
        for new_entity in json_results:
            for entity in alert_entities:
                if new_entity.strip() == entity.identifier.strip():
                    entity.additional_properties.update(enrichment_json)
                    updated_entities.append(entity)
                    output_message += "Enrichment added for entity: {}.\n".format(entity.identifier)
                    break
        siemplify.update_entities(updated_entities)
    siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_results))
    siemplify.result.add_json("Json", json_results)

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()