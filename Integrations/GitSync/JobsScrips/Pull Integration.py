from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler

SCRIPT_NAME = "Pull Integration"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    pull_whitelist = list(filter(None, [x.strip() for x in siemplify.extract_job_param("Install Whitelist", " ").split(',')]))

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for integration in pull_whitelist:
            siemplify.LOGGER.info(f"Pulling {integration}")
            integration = gitsync.content.get_integration(integration)
            if integration:
                siemplify.LOGGER.info(f"Installing {integration.identifier}")
                gitsync.install_integration(integration)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
