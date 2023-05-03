import base64
import json
from zipfile import ZipFile

from jinja2 import Environment as JinjaEnvironment
from jinja2 import Template

from constants import *


class File:
    """Represents a common file object used by the GitManager"""
    def __init__(self, path, contents):
        self.path = path
        if isinstance(contents, str):
            contents = contents.encode("utf-8")
        self.content = contents

    def __repr__(self):
        return f"{{Path: {self.path} Contents head: {self.content[:15]}...}}"

class Connector:
    def __init__(self, connector):
        self.raw_data = connector
        for param in self.raw_data['params']:
            param["creationTimeUnixTimeInMs"] = 0
            param["modificationTimeUnixTimeInMs"] = 0
        self.name = self.raw_data.get("displayName")
        self.description = self.raw_data.get("description")
        self.integration = self.raw_data.get("integration")
        self.integration_version = self.raw_data.get("integrationVersion")
        self.connector_definition_name = self.raw_data.get("connectorDefinitionName")
        self.environment = self.raw_data.get("environment")

    def create_readme(self, additionalInfo=""):
        if additionalInfo:
            readme = Template(CONNECTOR_README + additionalInfo)
        else:
            readme = Template(CONNECTOR_README)
        self.readme = readme.render(connector=self.raw_data)

    def iter_files(self):
        yield File("README.md", self.readme)
        yield File(f"{self.name}.json", json.dumps(self.raw_data, indent=4))


class VisualFamily:
    def __init__(self, visualFamily):
        if "visualFamilyDataModel" in visualFamily:
            visualFamily = visualFamily["visualFamilyDataModel"]
        self.raw_data = visualFamily
        self.name = self.raw_data.get("family")
        self.description = self.raw_data.get("description")
        self.imageBase64 = self.raw_data.get("imageBase64")
        self.rules = self.raw_data.get("rules")
        self.raw_data['id'] = 0
        for rule in self.raw_data["rules"]:
            rule["id"] = 0

    def get_importable(self):
        return {"visualFamilyDataModel": self.raw_data}

    def iter_files(self):
        yield File(f"{self.name}.json", json.dumps(self.get_importable(), indent=4))
        yield File("README.md", self.readme)
        yield File(f"{self.name}.png", base64.b64decode(self.imageBase64))

    def create_readme(self, additionalInfo=None):
        if additionalInfo:
            readme = Template(VISUAL_FAMILY_README + additionalInfo)
        else:
            readme = Template(VISUAL_FAMILY_README)
        self.readme = readme.render(visual_family=self.__dict__)


class Mapping:
    def __init__(self, integrationName, records, rules):
        self.integrationName = integrationName
        self.records = records
        self.rules = rules
        for rec in self.records:
            rec["id"] = 0
            rec["familyId"] = 0
        for rule in self.rules:
            for fam_fields in rule["familyFields"] + rule["systemFields"]:
                fam_fields["mappingRule"]["id"] = 0
                fam_fields["mappingRule"]["creationTimeUnixTimeInMs"] = 0
                fam_fields["mappingRule"]["modificationTimeUnixTimeInMs"] = 0
                fam_fields["creationTimeUnixTimeInMs"] = 0
                fam_fields["modificationTimeUnixTimeInMs"] = 0

    def iter_files(self):
        yield File(f"{self.integrationName}_Records.json", json.dumps(self.records, indent=4))
        yield File(f"{self.integrationName}_Rules.json", json.dumps(self.rules, indent=4))
        yield File(f"README.md", self.readme)

    def create_readme(self, additionalInfo=""):
        if additionalInfo:
            readme = Template(MAPPING_README + additionalInfo)
        else:
            readme = Template(MAPPING_README)
        self.readme = readme.render(mappings=self.__dict__)


class Integration:
    def __init__(self, integration_card, zip_buffer):
        self.zip_buffer = zip_buffer
        self.integration_card = integration_card

        self.zipfile = ZipFile(zip_buffer)
        self.identifier = self.integration_card.get("identifier")
        self.isCustom = self.integration_card.get("isCustomIntegration")
        self.definition = json.loads(self.zipfile.read(f"Integration-{self.identifier}.def"))
        self.version = self.definition.get("Version")
        if not self.isCustom:
            self.definition["IsCustom"] = False

        files = [x for x in self.zipfile.namelist() if not x.endswith("/")]
        self.actions = [json.loads(self.zipfile.read(x)) for x in files if x.startswith("ActionsDefinitions")]
        self.jobs = [json.loads(self.zipfile.read(x)) for x in files if
                     x.startswith("Jobs") and not x.startswith('JobsScrips')]
        self.connectors = [json.loads(self.zipfile.read(x)) for x in files if
                           x.startswith("Connectors") and not x.startswith('ConnectorsScripts')]
        if not self.isCustom:
            self.managers = [json.loads(self.zipfile.read(x)) for x in files if
                             x.startswith("Managers") and x.endswith(".managerdef")]
        else:
            self.managers = [x for x in files if x.startswith("Managers")]
        self.dependencies = [x for x in files if x.startswith("Dependencies")]
        self.resources = any([x.startswith("Resources/" + self.identifier + ".svg") for x in files])

    def create_readme(self, additionalInfo=""):
        env = JinjaEnvironment()
        env.filters.update({
            "action_param_type": lambda x: ACTION_PARAMETER_TYPES.get(x),
            "base_param_type": lambda x: BASE_PARAMETER_TYPES.get(x)
        })
        if additionalInfo:
            readme = env.from_string(INTEGRATION_README_TEMPLATE + additionalInfo)
        else:
            readme = env.from_string(INTEGRATION_README_TEMPLATE)
        if not self.isCustom:
            integration = {
                "dependencies": [],
                "definition": self.definition,
                "actions": filter(lambda x: x["IsCustom"], self.actions),
                "jobs": filter(lambda x: x["IsCustom"], self.jobs),
                "connectors": filter(lambda x: x["IsCustom"], self.connectors),
                "resources": self.resources
            }
            self.readme = readme.render(integration=integration)
        else:
            self.readme = readme.render(integration=self.__dict__)

    def __repr__(self):
        return self.identifier

    def iter_files(self, api):
        """
        Iterates all files in integration. If the integration is custom, it will only return custom and mandatory files.
        if not, it will iterate all the files in the exported zip. It yields tuples of (relative_path, data)
        :param api: SiemplifyApiClient object - to diff between custom and commercial scripts
        """
        if not self.isCustom:
            yield File(f"Integration-{self.identifier}.def", json.dumps(self.definition, indent=4))
            yield File("README.md", self.readme)

            if self.resources:
                for file in self.zipfile.namelist():
                    if file.startswith("Resources/") and not file.endswith("/"):
                        yield File(file, self.zipfile.read(file))

            for card in self.integration_card["cards"]:
                if card["isCustom"]:
                    definition = api.get_ide_item(card["id"], card["type"])
                    definition["id"] = 0

                    if card["type"] == ScriptType.ACTION:
                        yield File(f"ActionsDefinitions/{card['name']}.actiondef", json.dumps(definition, indent=4))
                        yield File(f"ActionsScripts/{card['name']}.py", self.zipfile.read(
                            f"ActionsScripts/{card['name']}.py").decode('utf-8'))

                    elif card["type"] == ScriptType.JOB:
                        try:
                            script_path = f"JobsScripts/{card['name']}.py"
                            script = self.zipfile.read(script_path).decode('utf-8')
                        except KeyError:
                            script_path = f"JobsScrips/{card['name']}.py"
                            script = self.zipfile.read(script_path).decode('utf-8')
                        yield File(script_path, script)
                        yield File(f"Jobs/{card['name']}.jobdef", json.dumps(definition, indent=4))

                    elif card["type"] == ScriptType.CONNECTOR:
                        yield File(f"Connectors/{card['name']}.connectordef", json.dumps(definition, indent=4))
                        yield File(f"ConnectorsScripts/{card['name']}.py", self.zipfile.read(
                            f"ConnectorsScripts/{card['name']}.py").decode('utf-8'))

                    elif card["type"] == ScriptType.MANAGER:
                        yield File(f"Managers/{card['name']}.managerdef", json.dumps(definition, indent=4))
                        yield File(f"Managers/{card['name']}.py", self.zipfile.read(
                            f"Managers/{card['name']}.py").decode(
                            'utf-8'))
        else:
            yield File("README.md", self.readme)
            for file in self.zipfile.namelist():
                content = self.zipfile.read(file)
                if content:  # filters folders
                    yield File(file, content)


class Playbook:
    def __init__(self, raw_data: dict):
        self.raw_data = raw_data
        self.raw_data["id"] = 0
        self.raw_data["trigger"]["id"] = 0
        self.name = self.raw_data.get("name")
        self.description = self.raw_data.get("description")
        self.type = PLAYBOOK_TYPES.get(self.raw_data.get("playbookType"))
        self.priority = self.raw_data.get("priority")
        self.isDebugMode = self.raw_data.get("isDebugMode", None)
        self.version = self.raw_data.get("version")
        self.trigger = self.raw_data.get("trigger")
        self.steps = self.raw_data.get("steps")
        self.isEnabled = self.raw_data.get("isEnabled")
        self.category = self.raw_data.get("categoryName", "Default")

    def create_readme(self, additionalInfo=""):
        env = JinjaEnvironment()
        env.filters.update({
            "trigger_type": lambda x: TRIGGER_TYPES.get(x),
            "condition_operator": lambda x: CONDITION_OPERATORS.get(x),
            "condition_match_type": lambda x: CONDITION_MATCH_TYPES.get(x),
            'split_action_name': lambda x: x.split("_")[1]
        })
        if additionalInfo:
            readme = env.from_string(PLAYBOOK_README_TEMPLATE + additionalInfo)
        else:
            readme = env.from_string(PLAYBOOK_README_TEMPLATE)
        self.readme = readme.render(playbook=self.__dict__,
                                    involved_blocks=[x for x in self.steps if x.get("actionName") == "NestedAction"])

    def iter_files(self):
        yield File(self.name + ".json", json.dumps(self.raw_data, indent=4))
        yield File("README.md", self.readme)


class Job:
    def __init__(self, raw_data: dict):
        raw_data["id"] = 0
        self.raw_data = raw_data
        self.name = self.raw_data.get("name")
        self.integration = self.raw_data.get("integration")
        self.description = self.raw_data.get("description")
        self.parameters = self.raw_data.get("parameters")
        self.runIntervalInSeconds = self.raw_data.get("runIntervalInSeconds")

    def create_readme(self, additionalInfo=""):
        env = JinjaEnvironment()
        env.filters.update({
            "base_param_type": lambda x: BASE_PARAMETER_TYPES.get(x)
        })
        if additionalInfo:
            readme = env.from_string(JOB_README + additionalInfo)
        else:
            readme = env.from_string(JOB_README)
        self.readme = readme.render(job=self.__dict__)

    def iter_files(self):
        yield File(f"Jobs/{self.name}.json", json.dumps(self.raw_data, indent=4))
