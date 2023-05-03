from SiemplifyAction import SiemplifyAction
import json

def update_alert_additional_data(siemplify, additional_data):
    siemplify.update_alerts_additional_data({siemplify.current_alert.identifier: json.dumps(additional_data)})

def main():
    siemplify = SiemplifyAction()
    
    in_string = siemplify.parameters.get("Json Fields")
    if in_string:
        try:
            data = json.loads(in_string)
        except:
            data = in_string
    else:
        data = None
    
    additional_data = siemplify.current_alert.additional_data
    if additional_data:
        alert_data = json.loads(additional_data)
        if "list" not in alert_data:
            alert_data["list"] = []
        if "dict" not in alert_data:
            alert_data["dict"] = {}
        if "data" not in alert_data:
            alert_data["data"] = ""
    else:
        alert_data = {"dict": {}, "list": []}
    
    if data:
        try:
            if isinstance(data, list):
                alert_data["list"].extend(data)
            elif isinstance(data, dict):
                alert_data["dict"].update(data)
            else:
                alert_data["data"] = data
        except:
            raise
        
        update_alert_additional_data(siemplify, alert_data)
    
    output_message = "Alert data attached as JSON to the action result"
    siemplify.result.add_result_json(alert_data)
    result_value = len(alert_data)
    
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
