from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import  output_handler, convert_dict_to_json_result_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyDataModel import CustomList
import json

    
def get_custom_list_items(siemplify, category_name, input_string):
        """
        Get a list of custom list items from category and entities list.
        :param category_name: the custom list category
        :param entities: a list of entities
        :return: a list of custom list item objects
        """

        custom_list_items = []
        custom_list_items.append(
            CustomList(input_string, category_name, siemplify.environment))
        return custom_list_items

def remove_entities_from_custom_list(siemplify, custom_list_items):
        """
        Remove the entities from the custom list with the given category.
        :param custom_list_items: a list of custom list items
        :return: None
        """
        custom_list_items_data = []
        for cli in custom_list_items:
            custom_list_items_data.append(cli.__dict__)

        address = "{0}/{1}".format(siemplify.API_ROOT, "external/v1/sdk/RemoveEntitiesFromCustomList?format=snake")
        response = siemplify.session.post(address, json=custom_list_items_data)
        siemplify.validate_siemplify_error(response)

        custom_list_dicts = response.json()

        # Create CustomList objects from the custom list dicts
        custom_lists = [CustomList(**custom_list_dict) for custom_list_dict in custom_list_dicts]
        return custom_lists        
        

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    try:
        status = EXECUTION_STATE_COMPLETED  
        output_message = "output message :" 
        result_value = 0 
        category = siemplify.parameters.get("Category")
        list_item = siemplify.parameters.get("ListItem")
        custom_list_items = get_custom_list_items(siemplify, category, list_item)
        json_result  = remove_entities_from_custom_list(siemplify, custom_list_items)
        output_message = "Removed {} from category {}".format(list_item, category)

    except Exception as e:
        raise
        status = EXECUTION_STATE_FAILED
        result_value = "Failed"
        output_message += "\n unknown failure"


    siemplify.end(output_message, True, status)


if __name__ == "__main__":
    main()
