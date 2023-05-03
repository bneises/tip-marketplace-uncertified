from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import bleach


def allow_attrs(tag, name, value):
    return True


@output_handler
def main():
    siemplify = SiemplifyAction()
    tags = list(filter(None, [x.strip() for x in
                         siemplify.extract_action_param("Tags", " ").split(',')]))
    attributes = list(filter(None, [x.strip() for x in
                         siemplify.extract_action_param("Attributes", " ").split(',')]))
    styles = list(filter(None, [x.strip() for x in
                         siemplify.extract_action_param("Styles", " ").split(',')]))                         
    input = siemplify.parameters.get("Input HTML")
    allow_all_tags = str(siemplify.extract_action_param(param_name="Allow All Tags",
                                                   is_mandatory=False,
                                                   print_value=False,
                                                   default_value='false')).lower() == 'true'
    allow_all_attrs = str(siemplify.extract_action_param(param_name="Allow All Attributes",
                                                   is_mandatory=False,
                                                   print_value=False,
                                                   default_value='false')).lower() == 'true'
    allow_all_styles = str(siemplify.extract_action_param(param_name="Allow All Styles",
                                                   is_mandatory=False,
                                                   print_value=False,
                                                   default_value='false')).lower() == 'true'
                                                   
    sanitized = ""    

   
    if tags and styles and attributes:
        sanatized = bleach.clean(input, tags=tags, styles=styles, attributes=attributes)
    elif tags and styles and allow_all_attrs:
        sanatized = bleach.clean(input, tags=tags, styles=styles, attributes=allow_attrs)
    elif tags and attributes and not styles:
        sanatized = bleach.clean(input, tags=tags, attributes=attributes)
    elif tags and allow_all_attrs and not styles:
        sanatized = bleach.clean(input, tags=tags, attributes=allow_attrs)
    elif tags and not styles and not attributes:
        sanatized = bleach.clean(input, tags=tags)
    elif styles and attributes and not tags:
        sanatized = bleach.clean(input, styles=styles, attributes=attributes)
    elif styles and allow_all_attrs and tags:
        sanatized = bleach.clean(input, styles=styles, attributes=allow_attrs)
    elif styles and not tags and not attributes and not allow_all_attrs:
        sanatized = bleach.clean(input, styles=styles)
    elif attributes and tags and not styles:
        sanatized = bleach.clean(input, tags=tags, attributes=attributes)
    elif attributes and styles and not tags and not allow_all_attrs:
        sanatized = bleach.clean(input,  attributes=attributes, styles=styles)
    elif attributes and not styles and not tags and not allow_all_attrs:
        sanatized = bleach.clean(input, attributes=attributes)
    elif allow_all_attrs and not tags and not styles:
        sanatized = bleach.clean(input, attributes=allow_attrs)
    else:
        sanatized = bleach.clean(input)
    result = sanatized
    output_message = "{0} successfully sanitized to: {1}".format(input, result)
    siemplify.end(output_message, result, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
