from ftplib import FTP
import subprocess
import datetime
import shutil
import sys
import os

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
RINEX_DST1 = f'C:\GNSS Spider\Data\RINEX\{STN_CODE}'
RINEX_DST2 = R'N:\RINEX'

RINEX_TEST1 = R"D:\test\rinex_test1"
RINEX_TEST2 = R"D:\test\rinex_test2"


# function to retrieve the current year
def get_year():
    return datetime.date.today().year


# setup ftp connection
year = get_year()  # get the current year
ftp = FTP(FTP_HOST)  # connect to ftp
ftp.login(FTP_USER, FTP_PASS)  # login to ftp
ftp.cwd('SD card/Data/Hourly')  # change working directory to location of data
ftp_list_unf = ftp.nlst()  # get list of filenames
dates_list = ftp.mlsd()  # get dates of files

# check if files in ftp are part of the current year
# this makes sure that julian days haven't rolled over
# from the previous year and are being placed in the wrong
# directory
ftp_list = []
for f, d in zip(ftp_list_unf, dates_list):
    if int(d[1]['modify'][0:4]) == year:  # check if timestamp of the file is the same as the current year
        ftp_list.append(f)  # append new list with only files from the current year
ftp_list.sort()  # sort filenames

# prepare data for filtering and cleaning
ftp_num_list = [os.path.splitext(f)[0][-4:-1] for f in ftp_list]  # get list of folder names
ftp_num_list.sort()  # sort folder name list
ftp_int_list = [int(f) for f in ftp_num_list]  # get integer values for folder list

# check if folder is created fro the current year, if not, make directory
if not os.path.exists(DST1 + '\\' + str(year)):
    os.mkdir(DST1 + '\\' + str(year))

# retrieve the most recently backed up folder name and julian day
try:
    last_dir = os.listdir(DST1 + '\\' + str(year)).pop()  # get the last folder created (most recent julian day for backup)
except IndexError:
    last_dir = 0  # if the list is empty (ie beginning of a new year), set value to 0

# check the amount of files in the last dir (back up missing files from most recent directory)
missing_files = 24 - len(os.listdir(DST1 + '\\' + str(year) + '\\' + last_dir))

# filter and clean up data
ftp_int_list = [int(f) for f in ftp_num_list if int(f) > int(last_dir)]  # find the index value for the files that have already been backed up
ftp_files_list = ftp_list[((len(ftp_list) - missing_files) - len(ftp_int_list)):]  # index files list to remove files that do not need to be copied
ftp_folder_list = [os.path.basename(f)[4:7] for f in ftp_files_list]  # parse string values in list for folder names
ftp_folder_list = list(set(ftp_folder_list))  # get unique values from list of folder names 
ftp_folder_list.sort()  # sort the folder names

# make the folders in the destination directory, copy files
for n in ftp_folder_list:
    folder = DST1 + '\\' + str(year) + '\\' + n  # create folder name as string
    if not os.path.exists(folder):  # if the folder doesn't exist already, make it
        os.mkdir(folder)
    for f in ftp_files_list:
        if f[4:7] == n:  # if the day in the filename matches the name of the folder, do some stuff
            try:
                filename = DST1 + '\\' + str(year) + '\\' + f[4:7] + '\\' + f  # create filename as string
                if not os.path.exists(filename):  # if the file doesnt exist, create it
                    with open(filename, 'wb') as fp:  # open a new file at output location with the same name
                        ftp.retrbinary(f'RETR {f}', fp.write)  # write bytes from source file to target file
            except:
                os.remove(filename)  # if exception occurs remove partially downloaded file
                sys.exit()  # quit program


# close ftp connection
ftp.close()

# copy files to second location
for f in ftp_folder_list:
    folder = DST1 + '\\' + str(year) + '\\' + f  # create folder name as string
    copy_str = f'Xcopy /E /I /Y {folder} "{DST2}' + '\\' + str(year) + '\\' + f'{f}"'  # create copy command as string
    subprocess.call(copy_str, shell=True)  # send copy string to command prompt and execute
# check if folder is created fro the current year, if not, make directory
rinex_path = RINEX_DST2 + '\\' + str(year)
if not os.path.exists(RINEX_DST2 + '\\' + str(year)):
    os.mkdir(rinex_path)
# convert files to rinex
for f in ftp_files_list:
    filename = DST1 + '\\' + str(year) + '\\' + f[4:7] + '\\' + f  # create filename as string
    rinex_name = rinex_path  + '\\' + f[4:7] + '\\' + '1_Dual' + '\\' + f'{STN_CODE}' + '\\' + f  # create filename as string
    no_ext = rinex_name.replace('.m00', '')  # remove filename extension
    # make directories for rinex output
    if not os.path.exists(rinex_path + '\\' + f[4:7]):
        os.mkdir(rinex_path  + '\\' + f[4:7])
    if not os.path.exists(rinex_path + '\\' + f[4:7] + '\\' + '1_Dual'):
        os.mkdir(rinex_path + '\\' + f[4:7] + '\\' + '1_Dual')
    if not os.path.exists(rinex_path + '\\' + f[4:7] + '\\' + '1_Dual' + '\\' + f'{STN_CODE}'):
        os.mkdir(rinex_path + '\\' + f[4:7] + '\\' + '1_Dual' + '\\' + f'{STN_CODE}')
    # execute file conversion
    teqc_str = f'{TEQC_PATH} +nav {no_ext}.{str(year)[-2:]}n {filename} > {no_ext}.{str(year)[-2:]}o'  # create teqc command as string
    subprocess.call(teqc_str, shell=True)  # send teqc string to command prompt and execute

# copy files to second location
for f in ftp_folder_list:
    folder = rinex_path + '\\' + f + '\\' + '1_Dual' + '\\' + f'{STN_CODE}'  # create folder name as string
    # make directories for copy destination of rinex files
    if not os.path.exists(RINEX_DST1 + '\\' + f'{year}'):
        os.mkdir(RINEX_DST1 + '\\' + f'{year}')
    if not os.path.exists(RINEX_DST1 + '\\' + f'{year}' + '\\' + f):
        os.mkdir(RINEX_DST1 + '\\' + f'{year}' + '\\' + f)
    copy_str = f'robocopy /E /I {folder} "{RINEX_DST1}' + '\\' + f'{year}' + '\\' + f'{f}' + '"'  # create copy command as string
    subprocess.call(copy_str, shell=True)  # send copy string to command prompt and execute
