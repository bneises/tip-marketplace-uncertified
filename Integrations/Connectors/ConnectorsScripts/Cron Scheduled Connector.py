from SiemplifyConnectors import SiemplifyConnectorExecution
from SiemplifyConnectorsDataModel import AlertInfo
from SiemplifyUtils import output_handler, unix_now
from SiemplifyConnectorsDataModel import CaseInfo
import SiemplifyUtils
import uuid
import sys
import json
import cronex
import datetime
VENDOR = "Siemplify"

@output_handler
def generate_alert(product_name, alert_name, alert_type, alert_fields):

    alert_id = str(uuid.uuid4())
    case_info = CaseInfo()
    case_info.events = []
    case_info.source_grouping_identifier = alert_id
    case_info.ticket_id = alert_id 
    case_info.display_id = alert_id 

    if alert_type:
        case_info.rule_generator = alert_type
    else:
        case_info.rule_generator = "Scheduled Alert"

    print(alert_name)
    if alert_name:
        case_info.name = alert_name
    else:
        case_info.name = "Scheduled Alert - " + alert_id
    
    case_info.device_product = product_name
    print('product_name - ' + product_name)
    for alert_field in alert_fields:
        case_info.extensions[alert_field.strip()] = alert_fields[alert_field]




    case_info.priority = 60  # Informative = -1,Low = 40,Medium = 60,High = 80,Critical = 100.
    case_info.start_time = SiemplifyUtils.unix_now()  # Times should be saved in UnixTime. You may use SiemplifyUtils DateTime conversions
    case_info.end_time = SiemplifyUtils.unix_now()

    case_info.device_vendor = VENDOR
    
    event = generate_event(case_info)
    case_info.events.append(event)

    return case_info


def generate_event(case_info):
    event = {}

    event["StartTime"] = SiemplifyUtils.unix_now()
    event["EndTime"] = SiemplifyUtils.unix_now()
    event["name"] = case_info.name
    event["event_type"] = case_info.rule_generator
    event["device_product"] = case_info.device_product  

    return event

@output_handler
def main():

    siemplify = SiemplifyConnectorExecution()  # Siemplify main SDK wrapper
    env_list = []
    
    product_name = siemplify.extract_connector_param("Product name")
    alert_name = siemplify.extract_connector_param("Alert name")
    alert_type = siemplify.extract_connector_param("Alert type")
    alert_fields_str = siemplify.parameters["Alert fields"]
    cron_expression = siemplify.parameters.get("Cron Expression")
    
    output_variables = {}
    log_items = []  #
    cases = []
    
    if cron_expression:
        job = cronex.CronExpression(cron_expression)
        now = datetime.datetime.now()
        if not job.check_trigger((now.year, now.month, now.day, now.hour, now.minute)):
            siemplify.LOGGER.info("Cron expression not matched")
        else:
            siemplify.LOGGER.info("Cron expression matched, processing case creation")

            alert_fields = json.loads(alert_fields_str)
        
            
            alert_obj = generate_alert(product_name, alert_name,alert_type,alert_fields)
            cases.append(alert_obj)
            print(json.dumps(cases[0].__dict__))
    siemplify.return_package(cases, output_variables, log_items)



if __name__ == "__main__":
    main()