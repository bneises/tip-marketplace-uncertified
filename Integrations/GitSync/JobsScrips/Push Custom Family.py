from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob
from SiemplifyUtils import output_handler
from definitions import VisualFamily

SCRIPT_NAME = "Push Custom Family"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    commit_msg = siemplify.extract_job_param("Commit")
    family_names = list(
        filter(None, [x.strip() for x in siemplify.extract_job_param("Family Name", " ").split(',')]))
    readme_addon = siemplify.extract_job_param("Readme Addon", input_type=str)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        for visualFamily in gitsync.api.get_custom_families():
            if visualFamily['family'] in family_names:

                if readme_addon:
                    siemplify.LOGGER.info("Readme addon found - adding to GitSync metadata file (GitSync.json)")
                    metadata = gitsync.content.get_metadata()
                    metadata["readmeAddons"]["Visual Family"][visualFamily.get("family")] = '\n'.join(
                        readme_addon.split("\\n"))
                    gitsync.content.push_metadata(metadata)

                siemplify.LOGGER.info(f"Pushing Visual Family - {visualFamily.get('family')}")
                gitsync.content.push_visual_family(VisualFamily(gitsync.api.get_custom_family(visualFamily['id'])))

        gitsync.commit_and_push(commit_msg)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise


if __name__ == "__main__":
    main()
