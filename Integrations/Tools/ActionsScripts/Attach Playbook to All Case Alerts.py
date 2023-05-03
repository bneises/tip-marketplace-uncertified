from SiemplifyUtils import output_handler
from SiemplifyAction import *

@output_handler
def main():
    siemplify = SiemplifyAction()
    
    workflow_name = siemplify.parameters["Playbook Name"]
    
    for alert in siemplify.case.alerts:
        alert_identifier = alert.identifier
        success = super(SiemplifyAction, siemplify).attach_workflow_to_case(workflow_name, siemplify.case_id, alert_identifier)
    if (str(success) == "True"):
        output_message = "Attached Playbook [%s] to all alerts in Case [%s]" % (workflow_name, siemplify.case_id)
    else:
        output_message = "Failed to attach Playbook [%s] to alerts in Case [%s]" % (workflow_name, siemplify.case_id)
    
    siemplify.end(output_message, str(success))

if __name__ == '__main__':
    main()
