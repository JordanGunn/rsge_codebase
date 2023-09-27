from typing import Union
import datetime


class TimeFormatString:

    """
    Enum class of datetime format strings (e.g. %Y-%m-%d -> 2022-02-25)
    """

    YEAR_MONTH_DAY_HYPSEP = "%Y-%m-%d"
    YEAR_MONTH_DAY_SLSHSEP = "%Y/%m/%d"
    YEAR_MONTH_DAY_SPCSEP = "%Y %m %d"
    DAY_MONTH_YEAR_HYPSEP = "%d-%m-%Y"
    DAY_MONTH_YEAR_SLSHSEP = "%d/%m/%Y"
    DAY_MONTH_YEAR_SPCSEP = "%d %m %Y"
    HOUR_MIN_SEC_CLNSEP = "%H:%M:%S"
    HOUR_MIN_SEC_SLSHSEP = "%H/%M/%S"
    HOUR_MIN_SEC_HYPSEP = "%H-%M-%S"


"""A tuple of the gps times where leap seconds were added"""
GPS_TIME_LEAP_SECONDS_ADDED = (
    46828800,  # Jun 30, 1981 - first leap second since start of GPS time
    78364801,  # Jun 30, 1982
    109900802,  # Jun 30, 1983
    173059203,  # Jun 30, 1985
    252028804,  # Dec 31, 1987
    315187205,  # Dec 31, 1989
    346723206,  # Dec 31, 1990
    393984007,  # Jun 30, 1992
    425520008,  # Jun 30, 1993
    457056009,  # Jun 30, 1994
    504489610,  # Dec 31, 1995
    551750411,  # Jun 30, 1997
    599184012,  # Dec 31, 1998
    820108813,  # Dec 31, 2005
    914803214,  # Dec 31, 2008
    1025136015,  # Jun 30, 2012
    1119744016,  # Jun 30, 2015
    1167264017  # Dec 31, 2016
)


"""Number of seconds between the start of unix time (Jan 1, 1970) and gps time (Jan 6, 1980)"""
UNIX_GPS_TIME_OFFSET_SECONDS = 315964800


def count_leaps(gps_time: Union[int, float]) -> int:
    """
    Count number of leap seconds that have passed.

    Leap seconds are added when necessary on
    June 30th, or December 31st.

    Official announcements of leap seconds are posted here:
    https://datacenter.iers.org/data/latestVersion/16_BULLETIN_C16.txt,
    but more user-friendly announcements exist with a simple Google search.
        - Last checked July, 2022 (there will be no leap second
        added at the end of December 2022, so the next possible leap second
        is June 30, 2023.)

    If a new leap second is added, convert it to GPS time here:
    https://www.andrews.edu/~tzs/timeconv/timeconvert.php,
    and add the value to the leaps tuple.

    e.g., enter Dec 31, 2016, 23:59:60 (UTC) to find gps time 1167264017.
    """

    n_leaps = 0
    for leap in GPS_TIME_LEAP_SECONDS_ADDED:
        if gps_time >= leap:
            n_leaps += 1

    return n_leaps


def gps2unix(time_value: Union[int, float], fmt_date: str = "%Y-%m-%d", fmt_time: str = "%H:%M:%S") -> str:

    """
    Convert GPS time to UNIX time.

    :param time_value: input gps time.
    :param fmt_time: format string for date (default='%Y-%m-%d')
    :param fmt_date: format string for time (default='%H:%M:%S')
    :return:
    """

    time = float(time_value)
    time += 1e9  # unadjusted gps time
    unix_time = time + UNIX_GPS_TIME_OFFSET_SECONDS - count_leaps(time)

    unix_time_str = datetime.datetime.fromtimestamp(unix_time).strftime(
        f'{fmt_date} {fmt_time}'
    )

    return unix_time_str


def today_str(fmt: str = "%Y-%m-%d") -> str:

    """
    Get today's date as a formatted string.

    Default format is '%Y-%m-%d'. Other formats contained within
    properties of TimeFormatString class may be passed as arguments.
    Additionally, string literals may be provided.

    :param fmt: format string for date (default='%Y-%m-%d')
    :return: Today's date as a string.
    """

    return datetime.datetime.today().strftime(fmt)
