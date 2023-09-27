
"""

  Converts time in adjusted GPS seconds (seconds since Jan 6, 1980 minus 1e9)
  to a date and time of day in local time.

"""
import pandas as pd
import datetime


def countleaps(gpsTime):
    """Count number of leap seconds that have passed."""

    # a tuple of the gps times where leap seconds were added
    leaps = (
        46828800, 78364801, 109900802, 173059203, 252028804,
        315187205, 346723206, 393984007, 425520008, 457056009,
        504489610, 551750411, 599184012, 820108813, 914803214,
        1025136015
    )

    nleaps = 0
    for leap in leaps:
        if gpsTime >= leap:
            nleaps += 1

    return nleaps


def convert_gps_time(time_value):

    # number of seconds between the start of unix time (Jan 1, 1970) and gps time (Jan 6, 1980)
    offset = 315964800

    time = float(time_value)
    time += 1e9 #unadjusted gps time
    unixtime = time + offset - countleaps(time)
    datetimestr = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return datetimestr


if __name__ == '__main__':
    df = pd.read_csv(R"D:\__code__\vscode\lasinfo\lidar_summary.csv")
        
    df['Start Time (PDT)'] = df['GPS Start'].map(convert_gps_time)
    df['End Time (PDT)'] = df['GPS End'].map(convert_gps_time)

    print(df.to_string())

    # df.to_csv('out.csv', index=False)

