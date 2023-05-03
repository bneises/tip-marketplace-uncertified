from SiemplifyUtils import output_handler
from SiemplifyAction import SiemplifyAction
import requests
import json
import time
from datetime import datetime
import base64
import re

CASE_MIN_URL = '{}/external/v1/cases/GetCaseFullDetails/{}'
ENTITY_INSIGHT_URL = '{}/external/v1/{}'
ACTION_NAME = "Get Case Data"
INSIGHT_CONTENT_RE = re.compile('<%\s(.*?)\s%>$')

def lowercase(x):
    lower = lambda in_str: in_str[:1].lower() + in_str[1:] if in_str else '' 
    if isinstance(x, list):
        return [lowercase(v) for v in x]
    elif isinstance(x, dict):
        return {lower(k): lowercase(v) for k, v in x.items()}
    else:
        return x
     
def get_insight_content(siemplify, insight):
    content_uri = INSIGHT_CONTENT_RE.match(insight['content']).group(1)
    insight_content_res = siemplify.session.get(ENTITY_INSIGHT_URL.format(siemplify.API_ROOT, content_uri))
    insight_content_res.raise_for_status()
    insight_content = lowercase(
                        json.loads(
                            base64.b64decode(
                                insight_content_res.json()
                                    .get('blob'))))
    return insight_content 
    
    
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    case_id = siemplify.extract_action_param("Case Id", default_value=siemplify.case_id, print_value=True)
    case_data = siemplify.session.get(CASE_MIN_URL.format(siemplify.API_ROOT, case_id))
    case_data.raise_for_status()
    
    case_json = case_data.json()
    if len(case_json['insights']) > 0:
        insights = []
        for insight in case_json['insights']:
            if insight['content'].startswith('<%') and insight['content'].endswith('%>'):
                content = get_insight_content(siemplify, insight)
                insights.append(content)
            else:
                insights.append(insight)
        case_json['insights'] = insights

    output_message = "success"
    siemplify.result.add_result_json(case_json)
    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info("\n output_message: {}".format( output_message))
    siemplify.end(output_message, True)

if __name__ == "__main__":
    main()