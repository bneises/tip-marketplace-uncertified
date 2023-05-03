from SiemplifyAction import SiemplifyAction
import json

def main():
    siemplify = SiemplifyAction()
    
    
    json_failure_message = ""
    if siemplify.parameters.get("JSON"):
        try:
            data = json.loads(siemplify.parameters.get("JSON"))
            siemplify.result.add_result_json(data)
            siemplify.result.add_json("Json", data)
        except Exception as e:
            json_failure_message = "Failed to load JSON with error: {}".format(e)
    
    output_message = "Input values 'transferred' to the output."
    if json_failure_message:
        output_message += "\n" + json_failure_message
    
    result_value = siemplify.parameters.get("ResultValue")
    
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
