from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED
from FileUtilitiesManager import EntityFileManager

# Example Consts:
INTEGRATION_NAME = "FileUtilities"

SCRIPT_NAME = "Add Entity to File"
FILE_PATH = u'/tmp/'
timeout = 200
@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    
    siemplify.LOGGER.info("================= Main - Param Init =================")
    
    
    filename = siemplify.extract_action_param(param_name="Filename", is_mandatory=False, print_value=True)
    
    output_message = ""
    result_value = True
    filepath = FILE_PATH + filename
    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        # Lock the file from other actions that may use it. if file 
        with EntityFileManager(filepath, timeout) as efm:
            for entity in siemplify.target_entities:
                if entity.identifier not in efm.entities:
                    siemplify.LOGGER.info("Adding entity: {}".format(entity.identifier))
                    efm.addEntity(entity.identifier)
                    output_message += "Added Entity: {}\n".format(entity.identifier)
                else:
                    siemplify.LOGGER.info("Entity is already in file: {}".format(entity.identifier))
                    output_message += "Entity is already in file: {}\n".format(entity.identifier)
                    result_value = False

    except Exception as e:
        siemplify.LOGGER.error("General error performing action {}".format(SCRIPT_NAME))
        siemplify.LOGGER.exception(e)
        raise


    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end(output_message, result_value, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()