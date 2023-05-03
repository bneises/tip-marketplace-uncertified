from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from definitions import Mapping, VisualFamily, Connector

SCRIPT_NAME = "Push Connector"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    commit_msg = siemplify.extract_job_param("Commit")
    connector_names = list(
        filter(None, [x.strip() for x in siemplify.extract_job_param("Connectors", " ").split(',')]))
    include_vf = siemplify.extract_job_param("Include Visual Families", input_type=bool)
    include_mappings = siemplify.extract_job_param("Include Mappings", input_type=bool)
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for connector in gitsync.api.get_connectors():
            if connector.get("displayName") in connector_names:
                siemplify.LOGGER.info(f"Pushing {connector.get('displayName')}")
                if readme_addon:
                    siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
                    metadata = gitsync.content.get_metadata()
                    metadata["readmeAddons"]["Connector"][connector.get("displayName")] = '\n'.join(
                        readme_addon.split("\\n"))
                    gitsync.content.push_metadata(metadata)

                gitsync.content.push_connector(Connector(connector))
                siemplify.LOGGER.info(f"Successfully pushed {connector.get('displayName')}")

                if include_mappings or include_vf:
                    integrationName = connector.get("integration")
                    records = [x for x in gitsync.api.get_ontology_records() if x.get("source") == integrationName]
                    visual_families = set([x.get("familyName") for x in records])
                    if include_mappings:
                        rules = []
                        for record in records:
                            record["exampleEventFields"] = []  # remove event assets
                            rule = gitsync.api.get_mapping_rules(record["source"], record["product"],
                                                                 record["eventName"])
                            for r in rule['familyFields'] + rule['systemFields']:
                                # remove bad rules with no source
                                if r['mappingRule']['source'] and r['mappingRule'][
                                    'source'].lower() == integrationName.lower():
                                    rules.append(rule)
                                    break
                        if not records and not rules:
                            siemplify.LOGGER.info(f"{integrationName} mappings don't exist. Skipping")
                        else:
                            siemplify.LOGGER.info(f"Pushing {integrationName} mappings")
                            gitsync.content.push_mapping(Mapping(integrationName, records, rules))

                    if include_vf:
                        for visualFamily in gitsync.api.get_custom_families():
                            if visualFamily['family'] in visual_families:
                                siemplify.LOGGER.info(f"Pushing Visual Family - {visualFamily['family']}")
                                gitsync.content.push_visual_family(
                                    VisualFamily(gitsync.api.get_custom_family(visualFamily['id'])))

        gitsync.commit_and_push(commit_msg)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise


if __name__ == "__main__":
    main()
