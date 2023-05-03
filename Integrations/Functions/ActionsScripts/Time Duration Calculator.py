from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from datetime import datetime, timezone
import pytz
# --------------------------------------------------------------------------------------------------
# Changes from Siemplify release,
# 2021-07-15 : MRodman - Added timezone awareness and correction if missing, seemed to cause issue with input_datetime1
# 2021-07-15 : MRodman - Added pytz import
# --------------------------------------------------------------------------------------------------
# Notes;
#       Time formats
#               Now = %Y-%m-%d %H:%M:%S.%f%z
#               2021-07-14T21:39:21Z = %Y-%m-%dT%H:%M:%SZ
# --------------------------------------------------------------------------------------------------


def getDuration(then, now=datetime.now(timezone.utc), interval="default"):
    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then  # For build-in functions
    duration_in_s = duration.total_seconds()

    def years():
        return divmod(duration_in_s, 31536000)  # Seconds in a year=31536000.

    def days(seconds=None):
        return divmod(seconds if seconds != None else duration_in_s, 86400)  # Seconds in a day = 86400

    def hours(seconds=None):
        return divmod(seconds if seconds != None else duration_in_s, 3600)  # Seconds in an hour = 3600

    def minutes(seconds=None):
        return divmod(seconds if seconds != None else duration_in_s, 60)  # Seconds in a minute = 60

    def seconds(seconds=None):
        if seconds != None:
            return divmod(seconds, 1)
        return duration_in_s

    def totalDuration():
        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        return "Time between dates: {} years, {} days, {} hours, {} minutes and {} seconds".format(int(y[0]), int(d[0]),
                                                                                                   int(h[0]), int(m[0]),
                                                                                                   int(s[0]))

    return {
        'years': int(years()[0]),
        'days': int(days()[0]),
        'hours': int(hours()[0]),
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()),
        'default': totalDuration()
    }[interval]


def tz_aware(dt):
    # date TZ awareness check function
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


@output_handler
def main():
    siemplify = SiemplifyAction()
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message :"  # human readable message, showed in UI as the action result
    result_value = None  # Set a simple result value, used for playbook if\else and placeholders.
    json_results = {}
    input_datetime1 = siemplify.extract_action_param("Input DateTime 1", print_value=True)
    input_datetime1_format = siemplify.extract_action_param("Input DateTime 1 Format", print_value=True)
    input_datetime2 = siemplify.extract_action_param("Input DateTime 2", print_value=True)
    input_datetime2_format = siemplify.extract_action_param("Input DateTime 2 Format", print_value=True)

    if input_datetime1 == "now":
        input_dt1 = datetime.now(timezone.utc)
        output_message += "Date Time 1 using now, which is {}\n".format(input_dt1)
    else:
        input_dt1 = datetime.strptime(input_datetime1, input_datetime1_format)
        output_message += "Date Time 1 is {}\n".format(input_dt1)
        if not tz_aware(input_dt1):
            output_message += "Date Time 1 not localized!, and will be corrected!\n"
            siemplify.LOGGER.info("Date Time 1 not localized!")
            input_dt1 = pytz.utc.localize(input_dt1)

    if input_datetime2 == "now":
        input_dt2 = datetime.now(timezone.utc)
        output_message += "Date Time 2 using now, which is {}\n".format(input_dt2)
    else:
        input_dt2 = datetime.strptime(input_datetime2, input_datetime2_format)
        output_message += "Date Time 2 is {}\n".format(input_dt2)
        if not tz_aware(input_dt2):
            output_message += "Date Time 2 not localized!, and will be corrected!\n"
            siemplify.LOGGER.info("Date Time 2 not localized!")
            input_dt2 = pytz.utc.localize(input_dt2)

    siemplify.LOGGER.info("Date Time 1 is {}\n".format(input_dt1))
    siemplify.LOGGER.info("Date Time 2 is {}\n".format(input_dt2))

    duration = getDuration(input_dt1, input_dt2)
    output_message += "Duration is {}\n".format(str(duration))

    json_results['years'] = getDuration(input_dt1, input_dt2, 'years')
    json_results['days'] = getDuration(input_dt1, input_dt2, 'days')
    json_results['hours'] = getDuration(input_dt1, input_dt2, 'hours')
    json_results['minutes'] = getDuration(input_dt1, input_dt2, 'minutes')
    json_results['seconds'] = getDuration(input_dt1, input_dt2, 'seconds')
    json_results['duration'] = duration
    siemplify.result.add_result_json(json_results)
    output_message = "The duration between {} and {} is {}".format(input_datetime1, input_datetime2,
                                                                   json_results['duration'])
    output_message += "calculation complete!\n.\n"
    result_value = json_results['seconds']
    siemplify.LOGGER.info(
        "\n  status: {}\n  result_value: {}\n  output_message: {}".format(status, result_value, output_message))
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
