from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
import json

def get_list_param(smp, param_name):
    param = smp.extract_action_param(param_name, " ")
    try:
        return set(json.loads(param))
    except:
        # Split by comma, Strip or convert to Int, filter None and empty strings, return set
        return set(filter(lambda v: v is not None and v is not "", [x.strip() if not x.isdigit() else int(x) for x in param.split(',')]))

@output_handler
def main():
    siemplify = SiemplifyAction()
    original = get_list_param(siemplify, "Original")
    subset = get_list_param(siemplify, "Subset")
    print(original, subset)

    result_value = subset <= original

    if result_value:
        output_message = "All items from the subset list are in the original list"
    else:
        output_message = f"Found items which are not in the original list: {','.join(sorted(str(x) for x in subset - original))}"

    siemplify.end(output_message, result_value)

if __name__ == "__main__":
    main()
