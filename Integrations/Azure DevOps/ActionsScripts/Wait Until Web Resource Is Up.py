import requests
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_INPROGRESS
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

SCRIPT_NAME = 'WaitUntilWebResourceIsUp'


def is_web_resource_up(url, should_include_content=None):
    resp = requests.get(url, timeout=5.0)

    if resp.ok and not should_include_content:
        return True

    if resp.ok and should_include_content and should_include_content.lower() in resp.text.lower():
        return True


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    result_value = False

    url = siemplify.extract_action_param(param_name='URL')

    siemplify.LOGGER.info('----------------- Main - Started -----------------')
    try:
        result_value = is_web_resource_up(url)
    except Exception as ex:
        siemplify.LOGGER.error('General error performing action {}'.format(SCRIPT_NAME))
        siemplify.LOGGER.exception(ex)

    siemplify.LOGGER.info('----------------- Main - Finished -----------------')

    status = EXECUTION_STATE_COMPLETED if result_value else EXECUTION_STATE_INPROGRESS
    output_message = 'Web resource {} is {}'.format(url, 'up' if result_value else 'down')
    siemplify.LOGGER.info(
            '\n  status: {}\n  result_value: {}\n  output_message: {}'.format(status, result_value, output_message)
    )
    siemplify.end(output_message, result_value, status)


if __name__ == '__main__':
    main()
