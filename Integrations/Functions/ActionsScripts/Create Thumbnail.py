from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
from PIL import Image
import io
import base64
import json
MISSING_VAL = "NotFound"
def find_key_path_in_json(key_path, json_data):
    """
    Finds the relevant key_path in a json object. 
    If list encountered, if its of len 1, its value is used. Otherwise, it exits with default value (MULTIPLE VALUES FOUND)
    """
    return find_key_path_recursive(key_path, json_data)
    
def find_key_path_recursive(key_list, current_json):
    if key_list:
        if isinstance(current_json, list):
            if key_list:
                if len(current_json) == 1:
                    return find_key_path_recursive(key_list, current_json[0])
                else:
                    return MULTIPLE_VALUES
            return ", ".join(current_json)
        if isinstance(current_json, dict):
            if key_list[0] in current_json:
                return find_key_path_recursive(key_list[1:], current_json[key_list[0]])
            # raise Exception("Key: {}, json: {}".format(key_list, current_json))
            return MISSING_VAL
    else:
        if isinstance(current_json, dict):
            raise Exception("Not a simple value.  Unable to enrich. Key: {}, json: {}".format(key_list, current_json))
        if isinstance(current_json, list):
            return u",".join(current_json)
        
        return u"{}".format(current_json) # Found val, return it. Format to make everything into string

def create_thumbnail(base64_str, thumb_size):
    buffer = io.BytesIO()
    
    imgdata = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(imgdata))
    new_img = img.resize((int(thumb_size[0]), int(thumb_size[1])))  # x, y
    new_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    return str(img_b64)[2:-1]
        
@output_handler
def main():
    siemplify = SiemplifyAction()
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    
    base64_str = siemplify.extract_action_param("Base64 Image", print_value=False)
    thumb_size = list(filter(None, [x.strip() for x in siemplify.parameters.get("Thumbnail Size").split(',')]))
    input_json = siemplify.extract_action_param("Input JSON", print_value=False)
    image_key_path = list(filter(None, [x.strip() for x in siemplify.parameters.get("Image Key Path").split('.')]))
    
    json_result = {}
    
    if input_json != None:
        in_json = json.loads(input_json)
        for entity_json in in_json:
            base64_str = find_key_path_in_json(image_key_path, entity_json)
            data = {}
            data['thumbnail'] = create_thumbnail(base64_str,thumb_size)
            json_result[entity_json['Entity']] = data
            json_result = convert_dict_to_json_result_dict(json_result)
    else:            
        data = {}
        data['thumbnail'] = create_thumbnail(base64_str, thumb_size)
        json_result = data
    
    siemplify.result.add_result_json(json_result)
    siemplify.LOGGER.info("\n  status: {}\n  result_value: {}\n  output_message: {}".format(status,result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
