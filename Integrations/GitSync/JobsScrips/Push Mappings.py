from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from definitions import Mapping

SCRIPT_NAME = "Push Mappings"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    commit_msg = siemplify.extract_job_param("Commit")
    source = siemplify.extract_job_param("Source")
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)
        siemplify.LOGGER.info(f"Pushing mappings of {source}")
        records = [x for x in gitsync.api.get_ontology_records() if x.get("source").lower() == source.lower()]
        rules = []
        for record in records:
            record["exampleEventFields"] = []  # remove event assets
            rule = gitsync.api.get_mapping_rules(record["source"], record["product"], record["eventName"])
            for r in rule['familyFields'] + rule['systemFields']:
                # remove bad rules with no source
                if r['mappingRule']['source'] and r['mappingRule']['source'].lower() == source.lower():
                    rules.append(rule)
                    break

        if readme_addon:
            siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
            metadata = gitsync.content.get_metadata()
            metadata["readmeAddons"]["Mappings"][source] = '\n'.join(
                readme_addon.split("\\n"))
            gitsync.content.push_metadata(metadata)

        gitsync.content.push_mapping(Mapping(source, records, rules))
        gitsync.commit_and_push(commit_msg)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise


if __name__ == "__main__":
    main()
