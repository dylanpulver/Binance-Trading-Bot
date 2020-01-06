import dateparser, pytz, sys, os
from datetime import datetime


def obtain_env_variable(variable_name, enviro_variable):
    """
    Obtains enviro variable and if not available exits script.

    Arguments:
        variable_name {string} -- the name of the variable in the script
        enviro_variable {string} -- the name the enviro variable is stored as
    """
    try:
        variable_name = os.environ.get(enviro_variable)
    except Exception as e:
        print(f"{enviro_variable} not set in environment")
        print(e)
        sys.exit(1)

    return variable_name


def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

# Example
#print(date_to_milliseconds("now UTC"))
#print(date_to_milliseconds("January 01, 2018"))
#print(date_to_milliseconds("11 hours ago UTC"))


def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms

# Examples

#print(interval_to_milliseconds('1m'))
#print(interval_to_milliseconds('30m'))
#print(interval_to_milliseconds('1w'))
