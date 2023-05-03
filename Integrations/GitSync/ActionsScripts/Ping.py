import re

from GitSyncManager import GitSyncManager
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from constants import COMMIT_AUTHOR_REGEX, DEFAULT_AUTHOR

SCRIPT_NAME = "Ping"
INTEGRATION_NAME = "GitSync"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    repo_url = siemplify.extract_configuration_param(INTEGRATION_NAME, "Repo URL")
    branch = siemplify.extract_configuration_param(INTEGRATION_NAME, "Branch")
    working_directory = GitSyncManager.get_working_dir(siemplify, repo_url)
    smpUsername = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Username")
    smpPassword = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Password")
    gitPassword = siemplify.extract_configuration_param(INTEGRATION_NAME, "Git Password/Token/SSH Key")
    gitUsername = siemplify.extract_configuration_param(INTEGRATION_NAME, "Git Username")
    gitUsername = gitUsername if gitUsername else "Not Relevant"
    gitAuthor = siemplify.extract_configuration_param(INTEGRATION_NAME, "Commit Author", default_value=DEFAULT_AUTHOR)
    if not re.fullmatch(COMMIT_AUTHOR_REGEX, gitAuthor):
        raise Exception("Commit Author parameter must be in the following format: James Bond <james.bond@gmail.com>")
    smpVerify = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Verify SSL", input_type=bool)
    gitVerify = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Verify SSL", input_type=bool)

    try:
        gitsync = GitSyncManager(siemplify, repo_url, branch, working_directory, smpUsername, smpPassword, gitPassword,
                                 gitUsername, gitAuthor, smpVerify, gitVerify)
    except Exception as e:
        raise Exception(f"Couldn't connect to git\nError: {e}")

    try:
        gitsync.api.get_bearer_token()
    except:
        raise Exception("Couln't connect to Siemplify. Check credentials")

    siemplify.end("True", True, 0)


if __name__ == "__main__":
    main()
