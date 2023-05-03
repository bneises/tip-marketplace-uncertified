from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler, add_prefix_to_dict
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import json, copy

from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

# CONSTS
MULTIPLE_VALUES = "MULTIPLE VALUES FOUND"
MISSING_VAL = "NotFound"
NOT_SIMPLE_VAL = "NOT A SIMPLE VALUE. ONLY SUPPORTS STRING"


def get_alert_entities(siemplify):
    return [entity for alert in siemplify.case.alerts for entity in alert.entities]
    
@output_handler
def main():
    siemplify = SiemplifyAction()

    json_data = siemplify.parameters.get("Enrichment JSON")
    enrichment_json = json.loads(json_data)  # we assume to have a list here
    key_path_raw = siemplify.parameters.get("Identifier KeyPath")
    separator = siemplify.parameters.get("Separator", ".")
    
    list_of_key_lists = [key_path.split(separator) for key_path in key_path_raw.split("\n")]
    prefix = siemplify.parameters.get("PrefixForEnrichment")
    enrichment_jsonpath = siemplify.parameters.get("Enrichment JSONPath", None)
    input_target_entities = list(filter(None, [x.strip() for x in siemplify.parameters.get("Target Entities", "").split(',')]))
    
    #use_scoping = siemplify.parameters.get("Use Entity Scoping", 'false').lower() == 'true'
    
    
    list_of_enrich_keys = []
    if enrichment_jsonpath:
        json_expression = parse(enrichment_jsonpath)
    #    list_of_enrich_keys = [key_path.split(separator) for key_path in enrichment_keypath.split("\n")]
    updated_entities = []
    
    target_entities = []
    #if use_scoping:
    target_entities = [entity for entity in siemplify.target_entities]
    #else:
    #    alert_entities = get_alert_entities(siemplify)
    #    for target_entity in input_target_entities:
    #        for entity in alert_entities:
    #            if entity.identifier == target_entity.upper():
    #                target_entities.append(entity)
    #                break
                    
    
        
    for entity in target_entities:
        for curr_enrich_json in enrichment_json:
            json_identifier = None
            for key_list in list_of_key_lists:
                json_identifier = find_key_path_in_json(key_list, curr_enrich_json)
                if json_identifier:
                    if json_identifier.upper() == entity.identifier.upper():
                        if enrichment_jsonpath:
                            enrich_dict = {}
                            match = json_expression.find(curr_enrich_json)
                            for m in match:
                                enrich_dict[str(m.path)] = m.value.encode('utf-8')
                            if prefix:
                                entity.additional_properties.update(add_prefix_to_dict(dict_to_flat(enrich_dict), prefix))
                            else:
                                entity.additional_properties.update(dict_to_flat(enrich_dict))
                            updated_entities.append(entity)
                            break # Exit JSON loop and continue to the next entity
                            
                            
                        if prefix:
                            
                            entity.additional_properties.update(add_prefix_to_dict(dict_to_flat(curr_enrich_json), prefix))
                        else:
                            
                            entity.additional_properties.update(dict_to_flat(curr_enrich_json))
                        updated_entities.append(entity)
                        break # Exit JSON loop and continue to the next entity
        
    count_updated_entities = len(updated_entities)
    
    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)

    siemplify.end('{0} entities were successfully enriched'.format(count_updated_entities), count_updated_entities, EXECUTION_STATE_COMPLETED)

def get_unicode(val):
    return str(val)

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

def dict_to_flat(target_dict):
    """
    Receives nested dictionary and returns it as a flat dictionary.
    :param target_dict: {dict}
    :return: Flat dict : {dict}
    """
    target_dict = copy.deepcopy(target_dict)

    def expand(raw_key, raw_value):
        key = raw_key
        value = raw_value
        """
        :param key: {string}
        :param value: {string}
        :return: Recursive function.
        """
        
        if value is None:
            return [(get_unicode(key), u"")]
        elif isinstance(value, dict):
            # Handle dict type value
            return [(u"{0}_{1}".format(get_unicode(key),
                                       get_unicode(sub_key)),
                     get_unicode(sub_value)) for sub_key, sub_value in dict_to_flat(value).items()]
        elif isinstance(value, list):
            # Handle list type value
            count = 1
            l = []
            items_to_remove = []
            for value_item in value:
                if isinstance(value_item, dict):
                    # Handle nested dict in list
                    l.extend([(u"{0}_{1}_{2}".format(get_unicode(key),
                                                     get_unicode(count),
                                                     get_unicode(sub_key)),
                               sub_value)
                              for sub_key, sub_value in dict_to_flat(value_item).items()])
                    items_to_remove.append(value_item)
                    count += 1
                elif isinstance(value_item, list):
                    l.extend(expand(get_unicode(key) + u'_' + get_unicode(count), value_item))
                    count += 1
                    items_to_remove.append(value_item)

            for value_item in items_to_remove:
                value.remove(value_item)

            for value_item in value:
                l.extend([(get_unicode(key) + u'_' + get_unicode(count), value_item)])
                count += 1

            return l
        else:
            
            return [(get_unicode(key), get_unicode(value))]

    items = [item for sub_key, sub_value in target_dict.items() for item in
             expand(sub_key, sub_value)]
    return dict(items)


if __name__ == "__main__":
    main()
