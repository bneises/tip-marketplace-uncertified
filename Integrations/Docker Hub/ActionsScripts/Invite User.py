from DockerHubManager import *
import traceback
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED


INTEGRATION_NAME = 'Docker Hub'
SCRIPT_NAME = 'Invite User'



@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    output_message = ''
    result_value = False
    status = EXECUTION_STATE_FAILED
    conf = siemplify.get_configuration(INTEGRATION_NAME)

    siemplify.LOGGER.info(u"----------------- Main - Param Init -----------------")
    username = conf['Username']
    password = conf["Password"]
    organization = siemplify.parameters['Organization']
    team = siemplify.parameters['Team']
    email = siemplify.parameters['Email']

    try:
        docker_client = DockerHub(username=username, password=password, delete_creds=True)
        docker_client.send_invite(organization, team, email)
        output_message += 'User has been invited to the Team!'
        result_value = True
        status = EXECUTION_STATE_COMPLETED
    except Exception:
        output_message += '{}'.format(traceback.format_exc())

    siemplify.LOGGER.info('\n  status: {}\n  result_value: {}\n  output_message: {}'.format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    main()
