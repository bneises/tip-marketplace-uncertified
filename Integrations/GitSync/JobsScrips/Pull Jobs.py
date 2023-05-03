from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob

SCRIPT_NAME = "Pull Jobs"


def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    jobNames = list(filter(None, [x.strip() for x in siemplify.extract_job_param("Job Whitelist", " ").split(',')]))

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for job in jobNames:
            siemplify.LOGGER.info(f"Pulling {job}")
            job = gitsync.content.get_job(job)
            gitsync.install_job(job)
            siemplify.LOGGER.info(f"Successfully pulled Job {job.name}")

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
