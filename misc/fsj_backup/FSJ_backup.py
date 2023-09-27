from ftplib import FTP
from tqdm import tqdm

import subprocess
import datetime
import sys
import os
import logging

"""
DESCRIPTION: This python scipt was created to copy data from the memory card of the fort st. john
GNSS receiver to the local machine used for storing and monitoring GNSS data at GeoBC. In the future,
if anything should change about the location of the data (e.g. the ftp host for the sd card of the receiver),
The constant values should be adjusted to reflect these changes. Additonally, the script will also convert
the copied data from the leica proprietary format (.00) to Rinex format. The program should run without any
input from the user, from any directory on your local computer (just double click to run). Finally, the code
has been set to run on the windows task scheduler at <<insert time here>> everyday, so unless it is necessary
to manually run the file, no human intervention should be needed.

Created by: Jordan Godau
Date: 2020-01-24
"""



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

error_log_dir = R'C:\backup_tools\FSJ_backup'

# TESTING DIRECTORIES. COMMENT OUT BEFORE BUILDING EXE
# DST2 = R"D:\test\__temp__\FSJ_GNSS_Backup\ftp"
# DST1 = R"D:\test\__temp__\FSJ_GNSS_Backup\local"
# error_log_dir = R'D:\test\__temp__\FSJ_GNSS_Backup'


log_file = os.path.join(error_log_dir,'FSJ_backup_errors.log')

# set up basic logging configuration
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# function to retrieve the current year
def get_year():
    return datetime.date.today().year


# setup ftp connection
year = get_year()  # get the current year
ftp = FTP(FTP_HOST, timeout=500)  # connect to ftp
ftp.login(FTP_USER, FTP_PASS)  # login to ftp
ftp.cwd("SD card/Data/Hourly")  # change working directory to location of data
ftp_list_unf = ftp.nlst()  # get list of filenames
dates_list = ftp.mlsd()  # get dates of files

# check if files in ftp are part of the current year
# this makes sure that julian days haven't rolled over
# from the previous year and are being placed in the wrong
# directory
ftp_list = []
for f, d in zip(ftp_list_unf, dates_list):
    if (
        int(d[1]["modify"][0:4]) == year
    ):  # check if timestamp of the file is the same as the current year
        ftp_list.append(f)  # append new list with only files from the current year
ftp_list.sort()  # sort filenames


# prepare data for filtering and cleaning
ftp_num_list = [
    os.path.splitext(f)[0][-4:-1] for f in ftp_list
]  # get list of folder names
ftp_num_list.sort()  # sort folder name list
ftp_int_list = [int(f) for f in ftp_num_list]  # get integer values for folder list

# check if folder is created fro the current year, if not, make directory
current_year_dir = os.path.join(DST1, str(year))

if not os.path.exists(current_year_dir):
    os.mkdir(current_year_dir)

# retrieve the most recently backed up folder name and julian day

try:
    last_dir = os.listdir(current_year_dir).pop()  # get the last folder created (most recent julian day for backup)
except IndexError:
    last_dir = 0  # if the list is empty (ie beginning of a new year), set value to 0


# check the amount of files in the last dir (back up missing files from most recent directory)
if os.path.isdir(os.path.join(current_year_dir, str(last_dir))):
    missing_files = 24 - len(os.listdir(DST1 + "\\" + str(year) + "\\" + last_dir))
else: 
    missing_files = 0


# filter and clean up data
ftp_int_list = [
    int(f) for f in ftp_num_list if int(f) > int(last_dir)
]  # find the index value for the files that have already been backed up
ftp_files_list = ftp_list[
    ((len(ftp_list) - missing_files) - len(ftp_int_list)) :
]  # index files list to remove files that do not need to be copied
ftp_folder_list = [
    os.path.basename(f)[4:7] for f in ftp_files_list
]  # parse string values in list for folder names
ftp_folder_list = list(
    set(ftp_folder_list)
)  # get unique values from list of folder names
ftp_folder_list.sort()  # sort the folder names

# print(ftp_files_list)
# make the folders in the destination directory, copy files
for n in ftp_folder_list:
    folder = DST1 + "\\" + str(year) + "\\" + n  # create folder name as string
    if not os.path.exists(folder):  # if the folder doesn't exist already, make it
        os.mkdir(folder)
    print(f"Backing up Julian Day {n}")
    for f in tqdm(ftp_files_list):
        if (
            f[4:7] == n
        ):  # if the day in the filename matches the name of the folder, do some stuff
            try:
                filename = (
                    DST1 + "\\" + str(year) + "\\" + f[4:7] + "\\" + f
                )  # create filename as string
                if not os.path.exists(filename):  # if the file doesnt exist, create it
                    with open(filename, "wb") as fp:  # open a new file at output location with the same name
                        ftp.retrbinary(f"RETR {f}", fp.write)  # write bytes from source file to target file
            except Exception as e:
                logging.error(f +'; '+ str(e))
                os.remove(filename)  # if exception occurs remove partially downloaded file
                ftp.close()
                sys.exit()  # quit program


# close ftp connection
ftp.close()

# copy files to second location
for f in ftp_folder_list:
    folder = DST1 + "\\" + str(year) + "\\" + f  # create folder name as string
    copy_str = (
        f'Xcopy /E /I /Y {folder} "{DST2}' + "\\" + str(year) + "\\" + f'{f}"'
    )  # create copy command as string
    subprocess.call(
        copy_str, shell=True
    )  # send copy string to command prompt and execute

# check if folder is created fro the current year, if not, make directory
# rinex_path = RINEX_DST2 + "\\" + str(year)
# if not os.path.exists(RINEX_DST2 + "\\" + str(year)):
#     os.mkdir(rinex_path)


# for f in ftp_files_list:
#     filename = (
#         DST1 + "\\" + str(year) + "\\" + f[4:7] + "\\" + f
#     )  # create filename as string
#     rinex_name = (
#         rinex_path + "\\" + f[4:7] + "\\" + "1_Dual" + "\\" + f"{STN_CODE}" + "\\" + f
#     )  # create filename as string
#     no_ext = rinex_name.replace(".m00", "")  # remove filename extension

#     # make directories for rinex output
#     if not os.path.exists(rinex_path + "\\" + f[4:7]):
#         os.mkdir(rinex_path + "\\" + f[4:7])
#     if not os.path.exists(rinex_path + "\\" + f[4:7] + "\\" + "1_Dual"):
#         os.mkdir(rinex_path + "\\" + f[4:7] + "\\" + "1_Dual")
#     if not os.path.exists(
#         rinex_path + "\\" + f[4:7] + "\\" + "1_Dual" + "\\" + f"{STN_CODE}"
#     ):
#         os.mkdir(rinex_path + "\\" + f[4:7] + "\\" + "1_Dual" + "\\" + f"{STN_CODE}")

#     # execute file conversion
#     # create teqc command as string
#     teqc_str = f"{TEQC_PATH} +nav {no_ext}.{str(year)[-2:]}n {filename} > {no_ext}.{str(year)[-2:]}o"  # create teqc command as strin
#     subprocess.call(
#         teqc_str, shell=True
#     )  # send teqc string to command prompt and execute
#     #########
#     # Edit the RINEX observation files
#     rinex_folder = rinex_path + "\\" + f[4:7] + "\\" + "1_Dual" + "\\" + f"{STN_CODE}"
#     # Go into the newly created folders holding the RINEX files
#     for item in os.listdir(rinex_folder):
#         if os.path.isfile(item):
#             # Find the observation files; they end in o
#             if item[-1] == "o":
#                 rinex_pth = os.path.join(rinex_folder, item)

#                 # Read the rinex observation file and edit the text as required
#                 with open(rinex_pth, "r") as rinex:
#                     filedata = rinex.readlines()
#                     filedata[
#                         7
#                     ] = "-Unknown-           LEIAR20         LEIM                    ANT # / TYPE\n"
#                     # Changing the approximate station coordinates to known true coordinates
#                     filedata[
#                         8
#                     ] = " -1816313.2809 -3053026.7217  5280285.9093                  APPROX POSITION XYZ\n"
#                 # Write all of the files lines, including the edited lines back into the original file
#                 with open(rinex_pth, "w") as f:
#                     f.writelines(filedata)
# #########
# # copy files to second location
# for f in ftp_folder_list:
#     folder = (
#         rinex_path + "\\" + f + "\\" + "1_Dual" + "\\" + f"{STN_CODE}"
#     )  # create folder name as string
#     # make directories for copy destination of rinex files
#     if not os.path.exists(RINEX_DST1 + "\\" + f"{year}"):
#         os.mkdir(RINEX_DST1 + "\\" + f"{year}")
#     if not os.path.exists(RINEX_DST1 + "\\" + f"{year}" + "\\" + f):
#         os.mkdir(RINEX_DST1 + "\\" + f"{year}" + "\\" + f)
#     copy_str = (
#         f'robocopy /E {folder} "{RINEX_DST1}' + "\\" + f"{year}" + "\\" + f"{f}" + '"'
#     )  # create copy command as string
#     subprocess.call(
#         copy_str, shell=True
#     )  # send copy string to command prompt and execute







# lazy fix to remove files from ftp location for GeoBC !!!!!!!!!!!!!!!!!!
# for x in ftp_backup_rinex:
#     os.remove(x)

