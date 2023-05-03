from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import requests, json, os.path, base64
from os import path

INTEGRATION_NAME = u"Imgbb"


@output_handler
def main():
    siemplify = SiemplifyAction()

    #Extracting the integration params
    conf = siemplify.get_configuration(INTEGRATION_NAME)
    api_key = conf.get("API Key")
    verify_ssl = conf.get('Verify SSL', 'false').lower() == 'true'
    
    v = requests.verify = verify_ssl
    
    url = 'https://api.imgbb.com/1/upload?expiration=600&key={0}'.format(api_key)
    
    #Extracting the action params- base64 image string
    image_file_path = siemplify.extract_action_param("Image File Path")
    

    #Initializing the json_result
    json_result = {}

    #Opening the file path from the directory and convert the image to base64
    with open(image_file_path , "rb") as image_file:
        image_base64_in_binary_string = base64.b64encode(image_file.read())
        image_in_base64 = image_base64_in_binary_string.decode('utf-8')

    #Determing the body params-for the request 
    data = {'image': image_in_base64}
    
    response = requests.post(url , data = data, verify =verify_ssl)
    
    response.raise_for_status()
    
    #Checking if the response content is in json format, otherwise it will raise an Exception
    try:
        response.json()
    except:
        raise Exception(response.content)
    
    #Place the image details in image_details variable
    image_details = response.json()

    #Getting the value of the image url
    image_url_link = image_details['data']['url']
    
    if not image_url_link:
        json_result['imageUrlLink']='None'
        output_message = "The URL link wasnt created"
        result_value = False
    
    #Checking the if image_url_link is None
    if image_url_link:
        json_result['imageUrlLink']=image_url_link
        output_message = "The image was uploaded successfully. Image URL is available in the action result"
        result_value = True
    
    else:
        json_result['error_message'] = image_details.get('message')
        output_message = "The URL link wasnt created" 
        result_value = False  

    #Adding the image URL link
    title = 'Image URL link'
    link = image_url_link
    siemplify.result.add_link(title, link)

    #Adding json result to the action
    siemplify.result.add_result_json(json_result)

    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
