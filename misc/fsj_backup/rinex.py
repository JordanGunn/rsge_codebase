from pathlib import Path
import datetime


teqc = R"D:\test\__temp__\FSJ_GNSS_Backup\teqc_mingw_64\teqc.exe"

raw_dir = Path(R'D:\test\__temp__\FSJ_GNSS_Backup\local\2020')

rinex_dir = Path(R'D:\test\__temp__\FSJ_GNSS_Backup\rinex')

raw_files = raw_dir.rglob('*.m00')

def get_year():
    return datetime.date.today().year

jul_days = {day.parts[-2] for day in raw_files}

for day in jul_days:
    rinex_day_dir = rinex_dir / day
    if not rinex_day_dir.is_dir():
        rinex_day_dir.mkdir(parents=True)


