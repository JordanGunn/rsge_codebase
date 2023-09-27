import datetime
from pathlib import Path
import logging
from ftplib import FTP
import ftputil


# constant values
STN_CODE = "BCFJ"
FTP_USER = "acp_fj"
FTP_PASS = "Nt04Pilot"
FTP_HOST = "96.53.120.66"
FTP_FULL_PATH = "ftp://" + FTP_HOST + "/SD%20Card/Data/Hourly"
TEQC_PATH = R"C:\Users\spider\Downloads\teqc_mingw_64\teqc.exe"
DST1 = f"N:\Data_Requests\{STN_CODE}_LEIAR20_LEIM_HI_=_0.003m"
DST2 = f"C:\GNSS Spider\Data\MDB\{STN_CODE}"
RINEX_DST1 = f"C:\GNSS Spider\Data\RINEX\{STN_CODE}"
RINEX_DST2 = R"N:\RINEX"

error_log_dir = R'C:\backup_tools\FSJ_backuFSJ_backup_errors.log'

# TESTING DIRECTORIES. COMMENT OUT BEFORE BUILDING EXE
DST2 = R"D:\test\__temp__\FSJ_GNSS_Backup\ftp"
DST1 = Path(R"D:\test\__temp__\FSJ_GNSS_Backup\local")
error_log_file = R'D:\test\__temp__\FSJ_GNSS_Backup\FSJ_backup_errors.log'

# set up basic logging configuration
logging.basicConfig(filename=error_log_file, level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# retrieve the current year
current_year = str(datetime.date.today().year)

def compare_file_size(file1: str, file2: str) -> bool:
    pass



with ftputil.FTPHost(FTP_HOST, FTP_USER, FTP_PASS) as ftp_host:
    ftp_host.chdir('SD Card/Data/Hourly')
    names = ftp_host.listdir(ftp_host.curdir)
    for name in names:
        out_parent_dir = name[4:7]
        outdir = DST1/current_year/out_parent_dir
        outfile = outdir/name

        outdir.mkdir(parents=True, exist_ok=True)
        
        if ftp_host.path.isfile(name):
            print(ftp_host.lstat(name).st_size)
            


            # print(f'Downloading {name}')
            # ftp_host.download_if_newer(name, outfile)
