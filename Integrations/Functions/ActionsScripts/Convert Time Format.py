from SiemplifyAction import *
import arrow
from dateutil import tz
import pytz

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main():
    siemplify = SiemplifyAction()
    siemplify.script_name='Convert Time Format'
    params = siemplify.parameters
    input_str = params.get('Input')
    from_format = params.get('From Format')
    to_format = params.get('To Format')
    time_delta_in_seconds = params.get('Time Delta In Seconds', 0) or 0
    timezone = params.get("Timezone")
    if from_format.endswith("UTC"):
        input_str, temp_tz = input_str.split("UTC")
        from_format = from_format.strip("UTC")
        time_delta_in_seconds = int(time_delta_in_seconds) - int(temp_tz) * 3600
    if from_format.endswith("GMT"):
        input_str, temp_tz = input_str.split("GMT")
        from_format = from_format.strip("GMT")
        time_delta_in_seconds = int(time_delta_in_seconds) - int(temp_tz) * 3600
    
    result_value = 'false'
    new_time = ''
    try:
        if not to_format:
            raise Exception("No output format")
        if not input_str:
            new_time = arrow.get()
        else:
            if is_number(input_str):
                if len(input_str) == 10:
                    new_time = arrow.get(int(input_str))
                elif len(input_str) == 13:
                    new_time = arrow.get(int(input_str) / 1000).replace(microsecond=(int(int(input_str) % 1000) * 1000))
                else:
                    try:
                        new_time = arrow.get(input_str)
                    except Exception:
                        siemplify.LOGGER.error("input is a timestamp, but badly formatted (not 10 or 13 digits)")
            else:
                new_time = arrow.get(arrow.Arrow.strptime(input_str, from_format))
    except Exception as e:
        siemplify.LOGGER.error(e)
        try:
            if is_number(input_str):
                if len(input_str) == 10:
                    new_time = arrow.get(int(input_str))
                elif len(input_str) == 13:
                    new_time = arrow.get(int(input_str) / 1000).replace(microsecond=(int(int(input_str) % 1000) * 1000))
                else:
                    try:
                        new_time = arrow.get(input_str)
                    except Exception:
                        siemplify.LOGGER.error("input is a timestamp, but badly formatted (not 10 or 13 digits)")
            else:
                new_time = arrow.get(arrow.Arrow.strptime(input_str, from_format))
            siemplify.LOGGER.info("Managed to process regardless of the provided format")
        except Exception:
            raise Exception("Could not process")
    if time_delta_in_seconds:
        #timezone = new_time.format("Z")
        new_time = new_time.shift(seconds=int(time_delta_in_seconds))
    if timezone:
        new_time = new_time.to(timezone)
    result_value = new_time.format(to_format)
    output_message = result_value
    siemplify.end(output_message, result_value)
if __name__ == "__main__":
    main()