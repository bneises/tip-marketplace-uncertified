from SiemplifyAction import SiemplifyAction
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_INPROGRESS
import arrow
import sys


SCRIPT_NAME ="Siemplify - Delay Playbook"

def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    seconds = int(siemplify.parameters.get('Seconds', 0))
    minutes = int(siemplify.parameters.get('Minutes', 0))
    hours = int(siemplify.parameters.get('Hours', 0))
    days = int(siemplify.parameters.get('Days', 0))

    target_date = arrow.utcnow().shift(seconds=seconds, minutes=minutes,
                                    hours=hours, days=days)

    siemplify.LOGGER.info(
        u"Waiting until {}".format(str(target_date.isoformat())))

    if target_date <= arrow.utcnow():
        # Reached target date
        siemplify.LOGGER.info(
            u"Reached target date {}".format(target_date.isoformat()))
        siemplify.end(u"Reached target date {}".format(target_date.isoformat()),
                      'true', EXECUTION_STATE_COMPLETED)

    else:
        siemplify.LOGGER.info(
            u"Hasn't reached the desired date {}. Current date: {}".format(
                target_date.isoformat(), arrow.utcnow().isoformat()))
        siemplify.end(
            u"Hasn't reached the desired date {}".format(target_date.isoformat()),
            target_date.isoformat(), EXECUTION_STATE_INPROGRESS)

def wait():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    try:
        target_date = arrow.get(siemplify.parameters["additional_data"])
    except: # order matters!
        try:
            target_date = arrow.get(siemplify.parameters["additional_data"], "M/D/YYYY H:mm:ss A")
        except:
            try:
                target_date = arrow.get(siemplify.parameters["additional_data"], "M/D/YYYY HH:mm:ss A")
            except:
                target_date = arrow.get(siemplify.parameters["additional_data"], "M/D/YYYY HH:mm:ss")

    if target_date <= arrow.utcnow():
        # Reached target date
        siemplify.LOGGER.info(
            u"Reached target date {}".format(target_date.isoformat()))
        siemplify.end(u"Reached target date {}".format(target_date.isoformat()),
                      'true', EXECUTION_STATE_COMPLETED)

    else:
        siemplify.LOGGER.info(
            u"Hasn't reached the desired date {}. Current date: {}".format(
                target_date.isoformat(), arrow.utcnow().isoformat()))
        siemplify.end(
            u"Hasn't reached the desired date {}".format(target_date.isoformat()),
            target_date.isoformat(), EXECUTION_STATE_INPROGRESS)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[2] == 'True':
        main()
    else:
        wait()
