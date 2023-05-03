from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED,EXECUTION_STATE_TIMEDOUT
import os
import glob

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    folder          = siemplify.extract_action_param("Folder", print_value=True)
    is_recursive    = siemplify.extract_action_param("Is Recursive", print_value=True)
    file_extension  = siemplify.extract_action_param("File Extension")
    files_num       = -1
    
    if not file_extension:
        file_extension = '*.*'
    full_path   = folder + '/' +  file_extension

    files       = glob.glob( full_path, recursive=is_recursive )
    files_num   = len( files ) 
    


    siemplify.end( files_num, files_num, EXECUTION_STATE_COMPLETED )


if __name__ == "__main__":
    main()