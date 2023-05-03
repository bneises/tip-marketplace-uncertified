from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
import json

ALERT_SCORE_INFO = 'ALERT_SCORE_INFO'
ALERT_SCORE = 'ALERT_SCORE'
ALERT_MAX_SCORE = 'ALERT_MAX_SCORE'
ALERT_SEVERITY = 'ALERT_SEVERITY'

SEVERITIES = {
    "Informational": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}
SEV_LIST = ['Informational', 'Low', 'Medium', 'High', 'Critical']

SCORING_THRESHOLDS = {
    "Low": 5,
    "Medium": 3,
    "High": 2
}


def category_exists(category, current_scores):
    for score_category in current_scores:
        if score_category['category'].lower() == category.lower():
            return True
    return False


def create_category_object(category, score=None, score_data=[]):
    if score:
        score_data.append(score)

    return {"category": category, "score_data": score_data}  # , "score": score_num, "max_score": max_score}


def compute_score(input_scores):
    comp_score = 0
    low_comp = 0
    med_comp = 0
    high_comp = 0
    if input_scores['Low'] > 0:
        comp_score = 1
    if input_scores['Low'] > SCORING_THRESHOLDS['Low']:
        low_comp = int(input_scores['Low'] / SCORING_THRESHOLDS['Low'])
        comp_score = 2
    if input_scores['Medium'] > 0:
        comp_score = 2
    if (input_scores['Medium'] + low_comp) > SCORING_THRESHOLDS['Medium']:
        med_comp = int((input_scores['Medium'] + low_comp) / SCORING_THRESHOLDS['Medium'])
        comp_score = 3
    if input_scores['High'] > 0:
        comp_score = 3
    if (input_scores['High'] + med_comp) > SCORING_THRESHOLDS['High']:
        high_comp = int((input_scores['High'] + med_comp) / SCORING_THRESHOLDS['High'])
        comp_score = 4
    if input_scores['Critical'] + high_comp > 0:
        comp_score = 4
    return comp_score


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "Add Alert Scoring Infomation"
    status = EXECUTION_STATE_COMPLETED

    score_name = siemplify.extract_action_param("Name")
    desc = siemplify.extract_action_param("Description")
    category = siemplify.extract_action_param("Category")
    severity = siemplify.extract_action_param("Severity")

    source = siemplify.extract_action_param("Source", "")
    case_tag = siemplify.parameters.get("Case Tag", None)
    current_score = 0
    result_value = "Informational"
    output_message = ""

    try:
        current_scoring = siemplify.get_alert_context_property(ALERT_SCORE_INFO).strip('"')
        current_scoring = json.loads(current_scoring)
    except:
        current_scoring = []

    try:
        found = 0
        new_score = {}
        new_score['score_name'] = score_name
        new_score['description'] = desc
        new_score['severity'] = severity
        new_score['score'] = SEVERITIES[severity]
        new_score['source'] = source
        total_scores = {'Informational': 0, 'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        updated_scores = []
        for _category in current_scoring:
            if _category['category'].lower() == category.lower():
                cat_obj = create_category_object(category, score=new_score, score_data=_category['score_data'])
                updated_scores.append(cat_obj)
                found = 1
                continue
            cat_obj = create_category_object(_category['category'], score_data=_category['score_data'])
            updated_scores.append(cat_obj)
        if len(current_scoring) == 0 or found == 0:
            cat_obj = create_category_object(category, score=new_score)
            updated_scores.append(cat_obj)

        for updated_category in updated_scores:
            updated_category['score_data'] = sorted(updated_category['score_data'],
                                                    key=lambda i: SEVERITIES[i['severity']], reverse=True)
            category_scores = {'Informational': 0, 'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
            for score in updated_category['score_data']:
                if score['severity'] == 'Informational':
                    total_scores['Informational'] += 1
                    category_scores['Informational'] += 1
                if score['severity'] == 'Low':
                    total_scores['Low'] += 1
                    category_scores['Low'] += 1
                if score['severity'] == 'Medium':
                    total_scores['Medium'] += 1
                    category_scores['Medium'] += 1
                if score['severity'] == 'High':
                    total_scores['High'] += 1
                    category_scores['High'] += 1
                if score['severity'] == 'Critical':
                    total_scores['Critical'] += 1
                    category_scores['Critical'] += 1
            updated_category['category_score'] = compute_score(category_scores)

        updated_scores = sorted(updated_scores, key=lambda i: i['category_score'], reverse=True)
        current_score_str = json.dumps(updated_scores)

        alert_score = compute_score(total_scores)

        updated_score = siemplify.set_alert_context_property(ALERT_SCORE_INFO, current_score_str)
        current_score_val = siemplify.set_alert_context_property(ALERT_SCORE, str(alert_score))
        alert_sev = siemplify.set_alert_context_property(ALERT_SEVERITY, SEV_LIST[alert_score])
        result_value = SEV_LIST[alert_score]


    except Exception as exception:
        siemplify.LOGGER.error("Unable to set alert score!")
        status = EXECUTION_STATE_FAILED
        output_message = "Unable to set alert score.\n"
        output_message += f"Exception: {type(exception).__name__}.\n"
        output_message += f"Exception message: {exception}.\n"
        raise

    siemplify.result.add_result_json(json.dumps(updated_scores))

    output_message = f"Alert Score with Name: {score_name}, Description: {desc}, category: {category}, score: {severity} has been added to the alert. The alert score is now: {SEV_LIST[alert_score]}."

    print(json.dumps(updated_scores, sort_keys=True))
    siemplify.end(output_message, SEV_LIST[alert_score], status)


if __name__ == "__main__":
    main()
