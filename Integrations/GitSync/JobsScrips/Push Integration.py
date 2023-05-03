from io import BytesIO

from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from definitions import Integration

SCRIPT_NAME = "Push Integration"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    push_whitelist = siemplify.extract_job_param("Push Whitelist").split(",")
    commit_msg = siemplify.extract_job_param("Commit")
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        integrations = [x for x in gitsync.api.get_ide_cards() if x['identifier'] in push_whitelist]

        for integration in integrations:
            siemplify.LOGGER.info(f"Pushing {integration['identifier']}")
            if readme_addon:
                siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
                metadata = gitsync.content.get_metadata()
                metadata["readmeAddons"]["Integration"][integration.get("identifier")] = '\n'.join(
                    readme_addon.split("\\n"))
                gitsync.content.push_metadata(metadata)
            integrationObj = Integration(integration, BytesIO(gitsync.api.export_package(integration["identifier"])))
            gitsync.content.push_integration(integrationObj)

        gitsync.commit_and_push(commit_msg)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
