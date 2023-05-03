# ============================================================================#
# title           :Change Case Name
# description     :This action will change the name of a case.  
# author          :robb@siemplify.co
# date            :2020-12-16
# python_version  :3.7
# libraries       :
# requirements     :
# product_version :1.0
# ============================================================================#
from SiemplifyAction import *
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "ChangeCaseName"
    
    output_message = ""
    result_value = "false"
    try:
        change = True
        siemplify.case.alerts.sort(key=lambda x: x.detected_time)
        if siemplify.parameters.get('Only If First Alert', 'false').lower() == 'true':
            if siemplify.current_alert.identifier != siemplify.case.alerts[0].identifier:
                change = False
        if change:
            res = siemplify.session.post('{}/external/v1/cases/RenameCase'.format(siemplify.API_ROOT),
                                        json={"caseId": siemplify.case_id, 
                                              "title": siemplify.parameters['New Name']})

        
            res.raise_for_status()
        
            output_message = "Case's title changed to: {}".format(siemplify.parameters['New Name'])
            result_value = 'true'
        else:
            output_message = "Case's title not changed, not first alert in the case"
            result_value = 'true'
    except Exception as e:
        output_message = "An error occured: " + e.message
        siemplify.LOGGER.error(output_message)
        siemplify.LOGGER.exception(e)
    
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
