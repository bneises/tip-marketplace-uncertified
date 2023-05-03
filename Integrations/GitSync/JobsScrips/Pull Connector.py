from GitSyncManager import GitSyncManager
from SiemplifyJob import SiemplifyJob

SCRIPT_NAME = "Pull Connector"


def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME

    connector_name = siemplify.extract_job_param("Connector Name")
    include_vf = siemplify.extract_job_param("Include Visual Families", input_type=bool)
    include_mappings = siemplify.extract_job_param("Include Mappings", input_type=bool)

    try:
        gitsync = GitSyncManager.from_siemplify_object(siemplify)

        connector = gitsync.content.get_connector(connector_name)
        if connector:
            siemplify.LOGGER.info(f"Installing Connector {connector_name}")
            gitsync.install_connector(connector)
            siemplify.LOGGER.info(f"Connector {connector_name} - successfully installed")

            if include_vf or include_mappings:
                mappings = gitsync.content.get_mapping(connector.integration)
                if mappings:
                    installed_visual_families = [x.get('family') for x in gitsync.api.get_custom_families(True)]
                    visual_families = set(
                        [x.get("familyName") for x in mappings.records if
                         x.get("familyName") not in installed_visual_families])

                    if include_vf:
                        siemplify.LOGGER.info(f"Installing Visual Families")
                        for vf in visual_families:
                            siemplify.LOGGER.info(f"Pulling visual family {vf}")
                            gitsync.api.add_custom_family(gitsync.content.get_visual_family(vf).raw_data)

                    if include_mappings:
                        siemplify.LOGGER.info(f"Installing Mappings")
                        gitsync.install_mappings(mappings)

    except Exception as e:
        siemplify.LOGGER.error("General error performing Job {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise

    siemplify.end_script()


if __name__ == "__main__":
    main()
