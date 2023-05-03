import json
import sys
import traceback

import requests
from ScriptResult import (EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,
                          EXECUTION_STATE_INPROGRESS)
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler

SCRIPT_NAME = 'Trigger Azure Build'
INTEGRATION = "Azure DevOps"
INVALID_BUILD_ID = -1

# Build statuses
BUILD_STATUS_ALL = 'all'
BUILD_STATUS_CANCELLING = 'cancelling'
BUILD_STATUS_COMPLETED = 'completed'
BUILD_STATUS_IN_PROGRESS = 'inProgress'
BUILD_STATUS_NONE = 'none'
BUILD_STATUS_NOT_STARTED = 'notStarted'
BUILD_STATUS_POSTPONED = 'postponed'

# Build results
BUILD_RESULT_CANCELED = 'canceled'
BUILD_RESULT_FAILED = 'failed'
BUILD_RESULT_NONE = 'none'
BUILD_RESULT_PARTIALLY_SUCCEEDED = 'partiallySucceeded'
BUILD_RESULT_SUCCEEDED = 'succeeded'


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.LOGGER.info('================= Main - Param Init =================')

    build_id = INVALID_BUILD_ID
    status = EXECUTION_STATE_INPROGRESS
    output_message = ''

    # Integration Params
    project_name = siemplify.extract_configuration_param(
        INTEGRATION, "Project")
    organization = siemplify.extract_configuration_param(
        INTEGRATION, "Organization")
    personal_access_token = siemplify.extract_configuration_param(
        INTEGRATION, "Personal Access Token")
    base_url = siemplify.extract_configuration_param(INTEGRATION, "Base URL")

    # Action Params
    definition_id = siemplify.extract_action_param(
        param_name='Build Definition Id')
    build_variables = siemplify.extract_action_param(
        param_name='Build Variables')

    siemplify.LOGGER.info('----------------- Main - Started -----------------')

    try:
        url = '{base_url}/{organization}/{project}/_apis/build/builds?api-version=5.1'.format(
            base_url=base_url,
            organization=organization,
            project=project_name)
        headers = {'Content-Type': 'application/json'}
        data = {
            'definition': {
                'id': definition_id
            },
            'parameters': build_variables
        }
        resp = requests.post(url, timeout=5.0, headers=headers, data=json.dumps(
            data), auth=('', personal_access_token))
        resp.raise_for_status()
        resp_json = resp.json()
        build_id = resp_json.get('id')
        output_message = 'A new Azure DevOps build <{build_id}> was triggered'.format(
            build_id=build_id)
        siemplify.LOGGER.info(output_message)
    except Exception as ex:
        siemplify.LOGGER.error(
            'General error performing action {}'.format(SCRIPT_NAME))
        siemplify.LOGGER.exception(ex)
        status = EXECUTION_STATE_FAILED
        output_message += '\nException occurred:\n{}'.format(
            traceback.format_exc())

    siemplify.LOGGER.info(
        '----------------- Main - Finished -----------------')
    siemplify.LOGGER.info(
        '\n  status: {}\n  result_value: {}\n  output_message: {}'.format(
            status, build_id, output_message)
    )
    siemplify.end(output_message, json.dumps({'build_id': build_id}), status)


def query_job():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    build_status = BUILD_STATUS_NONE
    build_result = BUILD_RESULT_NONE

    # Integration Params
    project_name = siemplify.extract_configuration_param(
        INTEGRATION, "Project")
    organization = siemplify.extract_configuration_param(
        INTEGRATION, "Organization")
    personal_access_token = siemplify.extract_configuration_param(
        INTEGRATION, "Personal Access Token")
    base_url = siemplify.extract_configuration_param(INTEGRATION, "Base URL")

    additional_data = siemplify.parameters['additional_data']
    additional_data_json = json.loads(additional_data)
    build_id = additional_data_json.get('build_id') or INVALID_BUILD_ID

    if build_id == INVALID_BUILD_ID:
        output_message = 'Invalid build id found'
        siemplify.end(output_message, BUILD_RESULT_FAILED,
                      EXECUTION_STATE_FAILED)

    siemplify.LOGGER.info(
        'Checking status of Azure DevOps build <{build_id}>'.format(build_id=build_id))
    url = '{base_url}/{organization}/{project}/_apis/build/builds/{build_id}?api-version=5.1'.format(
        base_url=base_url,
        organization=organization,
        project=project_name,
        build_id=build_id)
    headers = {'Content-Type': 'application/json'}
    try:
        resp = requests.get(url, timeout=5.0, headers=headers, auth=(
            'siemplify', personal_access_token))
        resp.raise_for_status()
        resp_json = resp.json()
        build_status = resp_json.get('status')
        build_result = resp_json.get('result')
    except Exception as ex:
        siemplify.LOGGER.error(
            'General error performing action {}'.format(SCRIPT_NAME))
        siemplify.LOGGER.exception(ex)
        siemplify.result.add_result_json(
            {'build_status': build_status, 'build_result': build_result, 'build_id': build_id})
        output_message = (
            'Error occurred on checking status of Azure DevOps build <{build_id}>:\n{ex}'
            .format(build_id=build_id, ex=ex)
        )
        siemplify.end(output_message, additional_data,
                      EXECUTION_STATE_INPROGRESS)
    else:
        siemplify.result.add_result_json(
            {'build_status': build_status,
                'build_result': build_result, 'build_id': build_id}
        )
        if not build_result or build_result == BUILD_RESULT_NONE:
            output_message = (
                'Waiting for the build result of Azure DevOps build <{build_id}>'
                .format(build_id=build_id)
            )
            siemplify.end(output_message, additional_data,
                          EXECUTION_STATE_INPROGRESS)
        else:
            output_message = (
                (
                    'Azure DevOps build <{build_id}> is finished with <{build_status}> status '
                    'and <{build_result}> result'
                )
                .format(build_id=build_id, build_status=build_status, build_result=build_result)
            )
            if build_result in (BUILD_RESULT_SUCCEEDED, BUILD_RESULT_PARTIALLY_SUCCEEDED):
                siemplify.end(output_message, build_result,
                              EXECUTION_STATE_COMPLETED)
            else:
                siemplify.end(output_message, build_result,
                              EXECUTION_STATE_FAILED)


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[2] == 'True':
        main()
    else:
        query_job()
