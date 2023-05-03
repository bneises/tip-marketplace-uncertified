import errno
import os
import re
import uuid
from base64 import b64encode

from jinja2 import Template

from GitContentManager import GitContentManager
from GitManager import Git
from Siemplify import Siemplify
from SiemplifyApiClient import SiemplifyApiClient
from constants import INTEGRATION_NAME, LOCAL_FOLDER, ROOT_README, DEFAULT_AUTHOR, COMMIT_AUTHOR_REGEX, \
    IGNORED_INTEGRATIONS
from definitions import File, Connector, Mapping, Integration, Playbook, Job, VisualFamily


class GitSyncManager:
    """
    GitSync manager holds the git client, Siemplify's API client and Git Content manager
    """
    def __init__(self,
                 siemplify: Siemplify,
                 repo_url: str,
                 branch: str,
                 working_directory: str,
                 smpUsername: str,
                 smpPassword: str,
                 gitPassword: str,
                 gitUsername: str = "None",
                 gitAuthor: str = DEFAULT_AUTHOR,
                 smpVerify: bool = False,
                 gitVerify: bool = False):
        self.logger = siemplify.LOGGER
        self.git_client = Git(repo_url, branch, working_directory, gitPassword, gitUsername, gitAuthor, gitVerify, self.logger)
        self.api = SiemplifyApiClient(siemplify.API_ROOT, siemplify.api_key, smpUsername, smpPassword, smpVerify)
        self.content = GitContentManager(self.git_client, self.api)
        self.cache = {}

    @classmethod
    def from_siemplify_object(cls, siemplify):
        """
        Init an instance by passing it the siemplify object

        :param siemplify: Siemplify object
        :return: GitSync instance
        """
        if siemplify.extract_job_param("Repo URL"):
            repoUrl = siemplify.extract_job_param("Repo URL")
        else:
            repoUrl = siemplify.extract_configuration_param(INTEGRATION_NAME, "Repo URL")

        if siemplify.extract_job_param("Branch"):
            branch = siemplify.extract_job_param("Branch")
        else:
            branch = siemplify.extract_configuration_param(INTEGRATION_NAME, "Branch")

        workingDirectory = GitSyncManager.get_working_dir(siemplify, repoUrl)
        smpUsername = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Username")
        smpPassword = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Password")
        gitPassword = siemplify.extract_configuration_param(INTEGRATION_NAME, "Git Password/Token/SSH Key")
        gitUsername = siemplify.extract_configuration_param(INTEGRATION_NAME, "Git Username")
        gitUsername = gitUsername if gitUsername else "Not Relevant"
        gitAuthor = siemplify.extract_configuration_param(INTEGRATION_NAME, "Commit Author", default_value=DEFAULT_AUTHOR)
        if not re.fullmatch(COMMIT_AUTHOR_REGEX, gitAuthor):
            raise Exception("Commit Author parameter must be in the following format: James Bond <james.bond@gmail.com>")
        smpVerify = siemplify.extract_configuration_param(INTEGRATION_NAME, "Siemplify Verify SSL", input_type=bool)
        gitVerify = siemplify.extract_configuration_param(INTEGRATION_NAME, "Git Verify SSL", input_type=bool)
        return cls(siemplify, repoUrl, branch, workingDirectory, smpUsername, smpPassword, gitPassword, gitUsername,
                   gitAuthor, smpVerify, gitVerify)

    @staticmethod
    def get_working_dir(siemplify: Siemplify, repo: str) -> str:
        """
        Gets the working Directory
        Will create the directory if does not exist.

        :param siemplify: Siemplify Object
        :param repo: Repo URL
        :return: folder path
        """
        if repo.endswith('/'):
            repo = repo.rstrip(repo[-1])

        repo_name = repo.rsplit('/', 1)[-1]
        folder_path = os.path.join(siemplify.RUN_FOLDER, LOCAL_FOLDER, repo_name)
        try:
            os.makedirs(folder_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        return folder_path

    @property
    def _marketplace_integrations(self):
        if "marketplace" not in self.cache:
            self.cache["marketplace"] = self.api.get_store_data()
        return self.cache["marketplace"]

    @property
    def _installed_playbooks(self):
        if "playbooks" not in self.cache:
            self.cache["playbooks"] = {x.get('name'): x for x in self.api.get_playbooks()}
        return self.cache["playbooks"]

    @property
    def _playbook_categories(self):
        if "categories" not in self.cache:
            self.cache["categories"] = {x.get('name'): x for x in self.api.get_playbook_categories()}
        return self.cache["categories"]

    def clear_cache(self):
        self.cache = {}

    def refresh_cache_item(self, item_name):
        del self.cache[item_name]

    def install_marketplace_integration(self, integration_name: str, required_version: str = None) -> bool:
        try:
            store_integration = next(
                x for x in self._marketplace_integrations if x["identifier"] == integration_name)
        except StopIteration:
            self.logger.warn(f"Integration {integration_name} wasn't found in the marketplace")
            return False
        if required_version and required_version != store_integration["version"]:
            self.logger.warn(f"Integration {integration_name} version mismatch - "
                             f"MP version: {store_integration['version']}, required version: {required_version}")
            return False
        self.api.install_integration(integration_name, store_integration["version"],
                                        store_integration["isCertified"])
        self.logger.info(f"{integration_name} installed successfully")
        return True

    def get_installed_integration_version(self, integration_name: str) -> float:
        try:
            return next(
                x["installedVersion"] for x in self._marketplace_integrations if x["identifier"] == integration_name)
        except StopIteration:
            self.logger.warn(f"Integration {integration_name} wasn't found in the marketplace")
            return 0.0

    def install_integration(self, integration: Integration, ignore_version_mismatch: bool = False):
        if integration.identifier in IGNORED_INTEGRATIONS:
            return
        self.logger.info(f"Installing {integration.identifier}")
        if integration.isCustom:
            self.logger.info(f"{integration.identifier} is a custom integration - importing as zip")
            self.api.import_package(integration.identifier,
                                       b64encode(integration.zip_buffer.getvalue()).decode('utf-8'))
        else:
            self.logger.info(f"{integration.identifier} is a commercial integration - Checking installation")
            if not self.get_installed_integration_version(integration.identifier):
                self.logger.info(f"{integration.identifier} is not installed - installing from the marketplace")
                if not self.install_marketplace_integration(integration.identifier, integration.version if not ignore_version_mismatch else None):
                    self.logger.warn(f"Couldn't install integration {integration.identifier} from the marketplace")
                    return
            integration_cards = next(x for x in self.api.get_ide_cards() if x["identifier"] == integration.identifier)['cards']
            for script in integration.actions + integration.jobs + integration.connectors + integration.managers:
                item_card = next((x for x in integration_cards if x["name"] == script["name"]), None)
                if item_card:
                    script["id"] = item_card["id"]
                    self.logger.info(
                        f"Updating {integration.identifier} - {script['name']}")
                else:
                    self.logger.info(
                        f"Adding {integration.identifier} - {script['name']}")
                self.api.update_ide_item(script)

    def install_connector(self, connector: Connector):
        installed_version = self.get_installed_integration_version(connector.integration)
        if not installed_version:
            self.logger.info(f"Connector {connector.name} integration ({connector.integration}) not installed")
            # Integration not installed - try installing from repo, and if not install from marketplace
            integration = self.content.get_integration(connector.integration)
            if integration and integration.isCustom:
                self.logger.info("Custom integration found in repo, installing")
                # Integration found in repo
                self.install_integration(integration)
            else:
                # Try installing integration from marketplace
                self.logger.info("Trying to install connector integration from the marketplace")
                if not self.install_marketplace_integration(connector.integration, connector.integration_version):
                    raise Exception(f"Error installing connector {connector.name} - missing integration")
                self.logger.info("Connector integration successfully installed from the marketplace")
        if connector.integration_version != installed_version:
            self.logger.warn("Installed integration version doesn't match the connector integration version. Please upgrade the connector.")
            connector.raw_data["isUpdateAvailable"] = True
        if connector.environment not in self.api.get_environment_names():
            self.logger.warn(f"Connector is set to non-existing environment {connector.environment}. Using Default Environment instead")
        self.api.update_connector(connector.raw_data)

    def install_mappings(self, mappings: Mapping, assign_vf: bool = True):
        self.logger.info(f"Installing mappings for {mappings.integrationName}")
        for rule in mappings.rules:
            self.api.add_mapping_rules(rule['familyFields'])
            self.api.add_mapping_rules(rule['systemFields'])

        if assign_vf:
            self.logger.info(f"Assigning visual families to integration mappings")
            for record in mappings.records:
                self.api.set_mappings_visual_family(record.get("source"), record.get("product"),
                                                    record.get("eventName"), record.get("familyName"))

    def install_playbook(self, playbook: Playbook):
        self.logger.info(f"Installing {playbook.name}")
        if playbook.name in self._installed_playbooks.keys():
            # Update playbook
            installed_playbook = self.api.get_playbook(self._installed_playbooks[playbook.name].get("identifier"))
            playbook.raw_data["id"] = installed_playbook.get("id")
            playbook.raw_data["identifier"] = installed_playbook.get("identifier")
            playbook.raw_data["originalPlaybookIdentifier"] = installed_playbook.get("originalPlaybookIdentifier")
            playbook.raw_data["trigger"]["id"] = installed_playbook.get("trigger").get("id")
            playbook.raw_data["trigger"]["identifier"] = installed_playbook.get("trigger").get("identifier")
            playbook.raw_data["categoryName"] = installed_playbook.get("categoryName")
            playbook.raw_data["categoryId"] = installed_playbook.get("categoryId")
        else:
            # New playbook
            playbook.raw_data["identifier"] = playbook.raw_data["originalPlaybookIdentifier"] = str(uuid.uuid4())
            playbook.raw_data["trigger"]["id"] = 0
            playbook.raw_data["trigger"]["identifier"] = str(uuid.uuid4())
            
            if playbook.category not in self._playbook_categories.keys():
                category = self.api.create_playbook_category(playbook.category)
                self.refresh_cache_item("categories")
            else:
                category = self._playbook_categories.get(playbook.category)
            
            playbook.raw_data["categoryId"] = category.get("id")

        self.api.save_playbook(playbook.raw_data)

    def install_job(self, job: Job):
        if not self.get_installed_integration_version(job.integration):
            self.logger.warn(f"Error installing job {job.name} - Job integration ({job.integration}) is not installed")
            return
        integration_cards = next((x for x in self.api.get_ide_cards() if x["identifier"] == job.integration), {}).get(
            'cards', None)
        if integration_cards:
            jobDefId = next((x for x in integration_cards if x["type"] == 2 and x["name"] == job.name), None)
            if jobDefId:
                job.raw_data["jobDefinitionId"] = jobDefId.get("id")

        jobId = next((x for x in self.api.get_jobs() if x["name"] == job.name), None)
        if jobId:
            job.raw_data["id"] = jobId.get("id")
        self.api.add_job(job.raw_data)

    def generate_root_readme(self) -> str:
        """
        Creates a readme file from all the components in the repo.

        :return: the readme file as string
        """
        stripNewLines = lambda x: x.replace("\n", "") if x else x

        get_connector_data = lambda connector: {"name": connector.name, "description": stripNewLines(connector.description),
                    "hasMappings": True if self.content.get_mapping(connector.integration) else False}

        get_integration_data = lambda integration: {"name": integration.definition["DisplayName"],
                    "description": stripNewLines(integration.definition["Description"])}

        get_jobs_data = lambda job: {"name": job.name, "description": stripNewLines(job.description)}

        get_visual_family_data = lambda vf: {"name": vf.name, "description": stripNewLines(vf.description)}

        get_playbook_data = lambda playbook: {"name": playbook.name, "description": stripNewLines(playbook.description)}

        connectors = [get_connector_data(x) for x in self.content.get_connectors()]
        integrations = [get_integration_data(x) for x in self.content.get_integrations()]
        jobs = [get_jobs_data(x) for x in self.content.get_jobs()]
        visual_families = [get_visual_family_data(x) for x in self.content.get_visual_families()]
        playbooks = [get_playbook_data(x) for x in self.content.get_playbooks()]

        readme = Template(ROOT_README)
        return readme.render(connectors=connectors, integrations=integrations, jobs=jobs,
                             visualFamilies=visual_families,
                             playbooks=playbooks)

    def update_readme(self, readme: str, basePath: str = ""):
        """
        Creates or updates a readme file in basePath

        :param readme: The readme content
        :param basePath: The base path - where to put the readme
        """
        if basePath and not basePath.endswith("/"):
            basePath += "/"
        self.git_client.update_objects([File(f"{basePath}README.md", readme)])

    def commit_and_push(self, message: str):
        """
        Commits all the changes and pushes the commit to the repo

        :param message: The commit message
        """
        # Generate root readme
        rootReadme = self.generate_root_readme()
        self.update_readme(rootReadme)

        self.git_client.commit_and_push(message)
