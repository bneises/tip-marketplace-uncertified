from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler

SCRIPT_NAME = "Pull Playbook"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    pull_whitelist = siemplify.extract_job_param("Playbook Whitelist").split(',')

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for playbook in pull_whitelist:
            siemplify.LOGGER.info(f"Pulling {playbook}")
            playbook = gitsync.content.get_playbook(playbook)
            gitsync.install_playbook(playbook)
            siemplify.LOGGER.info(f"Successfully installed {playbook.name}")

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
