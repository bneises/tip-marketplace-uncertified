from jinja2 import Template

from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from constants import PLAYBOOKS_ROOT_README
from definitions import Playbook

SCRIPT_NAME = "Push Playbook"


def create_root_readme(gitsync: GitSyncManager):
    playbooks = []
    for pb in gitsync.content.get_playbooks():
        playbooks.append(pb.raw_data)
    readme = Template(PLAYBOOKS_ROOT_README)
    return readme.render(playbooks=playbooks)


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME
    playbooks_whitelist = list(
        filter(None, [x.strip() for x in siemplify.extract_job_param("Playbook Whitelist", " ").split(',')]))
    folders_whitelist = list(
        filter(None, [x.strip() for x in siemplify.extract_job_param("Folders Whitelist", " ").split(',')]))
    commit_msg = siemplify.extract_job_param("Commit")
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for playbook in gitsync.api.get_playbooks():
            if playbook.get("name") in playbooks_whitelist or playbook.get("categoryName") in folders_whitelist:
                siemplify.LOGGER.info(f"Pushing {playbook['name']}")

                if readme_addon:
                    siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
                    metadata = gitsync.content.get_metadata()
                    metadata["readmeAddons"]["Playbook"][playbook.get("identifier")] = '\n'.join(
                        readme_addon.split("\\n"))
                    gitsync.content.push_metadata(metadata)

                playbookData = gitsync.api.get_playbook(playbook.get("identifier"))
                gitsync.content.push_playbook(Playbook(playbookData))

        gitsync.update_readme(create_root_readme(gitsync), "Playbooks")
        gitsync.commit_and_push(commit_msg)


    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
