from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob

SCRIPT_NAME = "Pull Mappings"


def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    source = siemplify.extract_job_param("Source")

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        siemplify.LOGGER.info(f"Pulling {source} Mappings")
        mappings = gitsync.content.get_mapping(source)
        gitsync.install_mappings(mappings, True)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
