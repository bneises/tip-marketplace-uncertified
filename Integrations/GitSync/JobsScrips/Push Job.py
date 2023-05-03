from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from constants import IGNORED_JOBS
from definitions import Job

SCRIPT_NAME = "Push Job"


def create_root_readme(gitsync: GitSyncManager):
    jobs = []
    for job in gitsync.content.get_jobs():
        job.create_readme(gitsync.content.get_metadata().get("readmeAddons", {}).get("Job", {}).get(job.name))
        jobs.append(job)

    readme = "".join([x.readme for x in jobs])
    gitsync.update_readme(readme, "Jobs")


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    commit_msg = siemplify.extract_job_param("Commit")
    jobs = list(filter(None, [x.strip() for x in siemplify.extract_job_param("Job Whitelist", " ").split(',')]))
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for job in gitsync.api.get_jobs():
            if job.get("name") in jobs and not job.get("name") in IGNORED_JOBS:
                siemplify.LOGGER.info(f"Pushing {job['name']}")
                job = Job(job)
                if readme_addon:
                    siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
                    metadata = gitsync.content.get_metadata()
                    metadata["readmeAddons"]["Job"][job.name] = '\n'.join(
                        readme_addon.split("\\n"))
                    gitsync.content.push_metadata(metadata)
                gitsync.content.push_job(job)

        create_root_readme(gitsync)

        gitsync.commit_and_push(commit_msg)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise


if __name__ == "__main__":
    main()
