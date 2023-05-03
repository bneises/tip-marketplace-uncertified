from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from operator import attrgetter

SCRIPT_NAME = "FindFirstAlert"

@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    siemplify.case.alerts.sort(key=lambda x: x.detected_time)
    output_message = f"First alert is: {siemplify.case.alerts[0].identifier} Created at: {siemplify.case.alerts[0].detected_time}\n"
    output_message += f"This alert is: {siemplify.current_alert.identifier}. Created at: {siemplify.current_alert.detected_time}\n\n"
    if siemplify.current_alert.identifier == siemplify.case.alerts[0].identifier:
        output_message += "This is the first alert."
        siemplify.end(output_message, siemplify.current_alert.identifier)
    output_message += "This is NOT the first alert."
    siemplify.end(output_message, "false")


if __name__ == "__main__":
    main()
