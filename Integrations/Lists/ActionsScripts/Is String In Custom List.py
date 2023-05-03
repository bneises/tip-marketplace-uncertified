from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import  output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyDataModel import CustomList
import json

def get_custom_list_items_from_identifier_list(siemplify, category_name, identifiers):
    """
    Get a list of custom list items from category and entities list.
    :param category_name: the custom list category
    :param identifiers: a list of strings
    :return: a list of custom list item objects
    """

    custom_list_items = []
    for identifier in identifiers:
        custom_list_items.append(
            CustomList(identifier, category_name, siemplify.environment))
    return custom_list_items

def is_identifier_in_custom_list(siemplify, identifier, category):
    # Returns True if identifier in category (for current environment)
    custom_list_items = get_custom_list_items_from_identifier_list(siemplify, category, [identifier])
    return siemplify.any_entity_in_custom_list(custom_list_items)


@output_handler
def main():
    siemplify = SiemplifyAction()
    
    try:
        status = EXECUTION_STATE_COMPLETED  
        output_message = "output message :" 
        result_value = 0 

        category = siemplify.parameters.get("Category")
        try:
            identifier_list = json.loads(siemplify.parameters.get("IdentifierList"))
        except:
            identifier_list = siemplify.parameters.get("IdentifierList").split(",")
        identifier_list = [x.strip() for x in identifier_list]
        
        json_result = {}
        for identifier in identifier_list:
            if is_identifier_in_custom_list(siemplify, identifier, category):
                json_result[identifier] = True
                result_value += 1
            else:
                json_result[identifier] = False
        
        if json_result:
            siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_result))
        
        output_message = "Found {} items in category {}".format(result_value, category)

    except Exception as e:
        raise
        status = EXECUTION_STATE_FAILED
        result_value = "Failed"
        output_message += "\n unknown failure"


    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
