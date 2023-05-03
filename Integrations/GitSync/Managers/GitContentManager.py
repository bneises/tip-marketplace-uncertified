import json
import stat
import zipfile
from io import BytesIO
from typing import List, Optional

from GitManager import Git
from SiemplifyApiClient import SiemplifyApiClient
from constants import METADATA
from definitions import Mapping, Integration, VisualFamily, Connector, Playbook, Job, File

INTEGRATIONS_PATH = "Integrations"
PLAYBOOKS_PATH = "Playbooks"
CONNECTORS_PATH = "Connectors"
JOBS_PATH = "Jobs"
MAPPINGS_PATH = "Ontology/Mappings"
VISUAL_FAMILIES_PATH = "Ontology/VisualFamilies"
METADATA_FILE = "GitSync.json"
SETTINGS_PATH = "Settings"
INTEGRATION_INSTANCES_FILE = f"{SETTINGS_PATH}/integrationInstances.json"
DYNAMIC_PARAMS_FILES = f"{SETTINGS_PATH}/dynamicParameters.json"
ENVIRONMENTS_FILE = f"{SETTINGS_PATH}/environments.json"
LOGO_FILE = f"{SETTINGS_PATH}/logo.json"
TAGS_FILE = f"{SETTINGS_PATH}/tags.json"
STAGES_FILE = f"{SETTINGS_PATH}/stages.json"
CASE_CLOSE_REASONS_FILE = f"{SETTINGS_PATH}/caseCloseCauses.json"
CASE_TITLES_FILE = f"{SETTINGS_PATH}/caseTitles.json"
NETWORKS_FILE = f"{SETTINGS_PATH}/networks.json"
DOMAINS_FILE = f"{SETTINGS_PATH}/domains.json"
CUSTOM_LISTS_FILE = f"{SETTINGS_PATH}/customLists.json"
EMAIL_TEMPLATES_FILE = f"{SETTINGS_PATH}/emailTemplates.json"
BLACKLIST_FILE = f"{SETTINGS_PATH}/blacklists.json"
SLA_DEFINITIONS_FILE = f"{SETTINGS_PATH}/slaDefinitions.json"


class GitContentManager:
    def __init__(self, git: Git, smpApi: SiemplifyApiClient):
        self.git = git
        self.smpApi = smpApi

    def get_metadata(self) -> dict:
        try:
            return json.loads(self.git.get_file_contents_from_path(METADATA_FILE))
        except KeyError:
            metadata = METADATA
            metadata["systemVersion"] = self.smpApi.get_system_version()
            self._push_file(METADATA_FILE, metadata)
            return metadata

    def push_metadata(self, metadata: dict):
        self._push_file(METADATA_FILE, metadata)

    def get_integration(self, integration_name: str) -> Optional[Integration]:
        '''
        Get integration as Integration object from the repo.

        :param integration_name: String. Integration name
        :return: an Integration object
        '''
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for file in self.git.get_file_objects_from_path(f"Integrations/{integration_name}"):
                    if file.path == f"Integration-{integration_name}.def":
                        definition = json.loads(file.content)
                    zip_file.writestr(file.path, file.content)
            zip_buffer.seek(0)
            return Integration({"identifier": integration_name, "isCustomIntegration": definition["IsCustom"]}, zip_buffer)
        except KeyError:
            return None

    def get_integrations(self) -> List[Integration]:
        try:
            for integration in self.git.get_raw_object_from_path(INTEGRATIONS_PATH).iteritems():
                if integration.mode == stat.S_IFDIR:
                    yield self.get_integration(integration.path.decode('utf-8'))
        except KeyError:
            return []

    def get_playbook(self, playbook_name: str) -> Optional[Playbook]:
        """
        Pulls a playbook or block from the repo

        :param playbook_name: Name of the playbook or block
        """
        try:
            for playbook in self.git.get_file_objects_from_path(PLAYBOOKS_PATH):
                if playbook.path.endswith(f"/{playbook_name}.json"):
                    return Playbook(json.loads(playbook.content))
        except KeyError:
            return None

    def get_playbooks(self) -> List[Playbook]:
        try:
            for playbook in self.git.get_file_objects_from_path(PLAYBOOKS_PATH):
                if playbook.path.endswith(".json"):
                    yield Playbook(json.loads(playbook.content))
        except KeyError:
            return []

    def get_connector(self, connector_name: str) -> Optional[Connector]:
        """
        Pulls a connector from the repo

        :param connector_name: Name of the connector
        :return: Connector json
        """
        try:
            for connector in self.git.get_file_objects_from_path(CONNECTORS_PATH):
                if connector.path.endswith(f"{connector_name}.json"):
                    return Connector(json.loads(connector.content))
        except KeyError:
            return None

    def get_connectors(self) -> List[Connector]:
        try:
            for connector in self.git.get_file_objects_from_path(CONNECTORS_PATH):
                if connector.path.endswith(".json"):
                    yield Connector(json.loads(connector.content))
        except KeyError:
            return []

    def get_job(self, job_name: str) -> Optional[Job]:
        try:
            return Job(json.loads(self.git.get_file_contents_from_path(f"{JOBS_PATH}/{job_name}.json")))
        except KeyError:
            return None

    def get_jobs(self) -> List[Job]:
        try:
            for job in self.git.get_file_objects_from_path(JOBS_PATH):
                if job.path.endswith(".json"):
                    yield Job(json.loads(job.content))
        except KeyError:
            return []

    def get_mapping(self, source_name) -> Optional[Mapping]:
        """
        Pulls a mapping from repo

        :param source_name: Source integration name
        :return: Mapping object
        """
        try:
            records = json.loads(
                self.git.get_file_contents_from_path(f"{MAPPINGS_PATH}/{source_name}/{source_name}_Records.json"))

            rules = json.loads(
                self.git.get_file_contents_from_path(f"{MAPPINGS_PATH}/{source_name}/{source_name}_Rules.json"))

            return Mapping(source_name, records, rules)
        except KeyError:
            return None

    def get_mappings(self) -> List[Mapping]:
        try:
            for mappings in self.git.get_raw_object_from_path(MAPPINGS_PATH):
                yield self.get_mapping(mappings.decode('utf-8'))
        except KeyError:
            return []

    def get_visual_family(self, family_name: str) -> Optional[VisualFamily]:
        """
        Pulls a visual family from repo

        :param family_name: Name of the family to pull from the repo
        :return:
        """
        try:
            return VisualFamily(json.loads(
                self.git.get_file_contents_from_path(f"{VISUAL_FAMILIES_PATH}/{family_name}/{family_name}.json")))
        except KeyError:
            return None

    def get_visual_families(self) -> List[VisualFamily]:
        try:
            for vf in self.git.get_raw_object_from_path(VISUAL_FAMILIES_PATH):
                yield self.get_visual_family(vf.decode('utf-8'))
        except KeyError:
            return []

    def get_integration_instances(self) -> List[dict]:
        return json.loads(self._get_file_or_default(INTEGRATION_INSTANCES_FILE, "[]"))

    def get_dynamic_parameters(self) -> List[dict]:
        return json.loads(self._get_file_or_default(DYNAMIC_PARAMS_FILES, "[]"))

    def get_environments(self) -> List[dict]:
        return json.loads(self._get_file_or_default(ENVIRONMENTS_FILE, "[]"))

    def get_logo(self) -> dict:
        return json.loads(self._get_file_or_default(LOGO_FILE, "{}"))

    def get_tags(self) -> List[dict]:
        return json.loads(self._get_file_or_default(TAGS_FILE, "[]"))

    def get_stages(self) -> List[dict]:
        return json.loads(self._get_file_or_default(STAGES_FILE, "[]"))

    def get_case_close_causes(self) -> List[dict]:
        return json.loads(self._get_file_or_default(CASE_CLOSE_REASONS_FILE, "[]"))

    def get_case_titles(self) -> List[dict]:
        return json.loads(self._get_file_or_default(CASE_TITLES_FILE, "[]"))

    def get_networks(self) -> List[dict]:
        return json.loads(self._get_file_or_default(NETWORKS_FILE, "[]"))

    def get_domains(self) -> List[dict]:
        return json.loads(self._get_file_or_default(DOMAINS_FILE, "[]"))

    def get_custom_lists(self) -> List[dict]:
        return json.loads(self._get_file_or_default(CUSTOM_LISTS_FILE, "[]"))

    def get_email_templates(self) -> List[dict]:
        return json.loads(self._get_file_or_default(EMAIL_TEMPLATES_FILE, "[]"))

    def get_blacklists(self) -> List[dict]:
        return json.loads(self._get_file_or_default(BLACKLIST_FILE, "[]"))

    def get_sla_definitions(self) -> List[dict]:
        return json.loads(self._get_file_or_default(SLA_DEFINITIONS_FILE, "[]"))

    def push_integration(self, integration: Integration):
        """
        Uploads an integration to git.

        :param integration: An integration object
        """
        integration.create_readme(
            self.get_metadata().get("readmeAddons", {}).get("Integration", {}).get(integration.identifier))
        self.git.update_objects(integration.iter_files(self.smpApi), base_path=f"{INTEGRATIONS_PATH}/{integration.identifier}".encode('utf-8'))

    def push_playbook(self, playbook: Playbook):
        """
        Pushes a playbook or block to the repo

        :param playbook: a Playbook object
        """
        self._push_obj(playbook, playbook.name, "Playbook",
                       f"{PLAYBOOKS_PATH}/{playbook.category}/{playbook.name}".encode('utf-8'))

    def push_connector(self, connector: Connector):
        """
        Pushes a connector to the repo

        :param connector: Connector json
        """
        self._push_obj(connector, connector.name, "Connector",
                       f"{CONNECTORS_PATH}/{connector.integration}/{connector.name}".encode('utf-8'))

    def push_job(self, job: Job):
        """
        Pushes a job to the repo

        :param job: a Job object
        """
        self.git.update_objects(job.iter_files())

    def push_mapping(self, mapping: Mapping):
        """
        Pushes an integration mappings

        :param mapping: Mapping object
        """
        self._push_obj(mapping, mapping.integrationName, "Mappings",
                       f"{MAPPINGS_PATH}/{mapping.integrationName}".encode('utf-8'))

    def push_visual_family(self, family: VisualFamily):
        """
        Pushes custom family

        :param family: VisualFamily object
        """
        self._push_obj(family, family.name, "Visual Family",
                       f"{VISUAL_FAMILIES_PATH}/{family.name}".encode('utf-8'))

    def push_integration_instances(self, integration_instances: List[dict]):
        self._push_file(INTEGRATION_INSTANCES_FILE, integration_instances)

    def push_dynamic_parameters(self, dynamic_parameters: List[dict]):
        self._push_file(DYNAMIC_PARAMS_FILES, dynamic_parameters)

    def push_environments(self, environments: List[dict]):
        self._push_file(ENVIRONMENTS_FILE, environments)

    def push_logo(self, logo: dict):
        self._push_file(LOGO_FILE, logo)

    def push_tags(self, tags: List[dict]):
        self._push_file(TAGS_FILE, tags)

    def push_stages(self, stages: List[dict]):
        self._push_file(STAGES_FILE, stages)

    def push_case_close_causes(self, close_causes: List[dict]):
        self._push_file(CASE_CLOSE_REASONS_FILE, close_causes)

    def push_case_titles(self, case_titles: List[dict]):
        self._push_file(CASE_TITLES_FILE, case_titles)

    def push_networks(self, networks: List[dict]):
        self._push_file(NETWORKS_FILE, networks)

    def push_domains(self, domains: List[dict]):
        self._push_file(DOMAINS_FILE, domains)

    def push_custom_lists(self, custom_lists: List[dict]):
        self._push_file(CUSTOM_LISTS_FILE, custom_lists)

    def push_email_templates(self, email_templates: List[dict]):
        self._push_file(EMAIL_TEMPLATES_FILE, email_templates)

    def push_blacklists(self, blacklists: List[dict]):
        self._push_file(BLACKLIST_FILE, blacklists)

    def push_sla_definitions(self, sla_definitions: List[dict]):
        self._push_file(SLA_DEFINITIONS_FILE, sla_definitions)

    def _get_file_or_default(self, path, default=None):
        try:
            return self.git.get_file_contents_from_path(path)
        except KeyError:
            return default

    def _push_obj(self, content, content_name, content_type, path):
        content.create_readme(self.get_metadata().get("readmeAddons", {}).get(content_type, {}).get(content_name))
        self.git.update_objects(content.iter_files(), base_path=path)

    def _push_file(self, path: str, content):
        self.git.update_objects([File(path, self._json_encoder(content))])

    def _json_encoder(self, d) -> str:
        return json.dumps(d, indent=4)
