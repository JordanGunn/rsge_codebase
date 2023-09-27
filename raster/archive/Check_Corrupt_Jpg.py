import gdal
import sys
import os
from itertools import chain
from tkinter import filedialog
from tkinter import Tk
import csv
import time
from pathlib import Path
start_time = time.time()
# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()

# Script will recursively go through subdirectories and report information about each tif image. If there is
# a corrupt image it will add an entry to a csv. place script in parent folder and run.

Tk().withdraw()

# Specify input and output directory
indir = filedialog.askdirectory(title='Select input directory')

os.chdir(indir)
path = Path(indir)

jpg = path.rglob('*.jpg')
jpeg = path.rglob('*.jpeg')
jpg_list = list(chain(jpg,jpeg))

for idx,image in enumerate(jpg_list, start=1):

    print("\r Checking file {} of {}".format(idx, len(jpg_list)), end='')  

    image = str(image)
    try:
        tif = gdal.Open(image)
        # print gtif.GetMetadata()
        statinfo = os.stat(image)
        size = statinfo.st_size / 1e6
        cols = tif.RasterXSize
        rows = tif.RasterYSize

        # print(image, ' -- ', size, 'Mb')
        # print size, "Mb"

        # print("     bands", tif.RasterCount, ' -- ', cols, "cols x ", rows, " rows")
        # print cols, " cols x ", rows, " rows"

        tif = None

    except RuntimeError as e:
        # print('Unable to open ' + image)
        # print(e)
        x = image, e
        with open('image_errors.csv', 'a') as csvfile:
            wr = csv.writer(csvfile, delimiter=',')
            wr.writerow(x)

if os.path.isfile('image_errors.csv'):
    print('\n\n!!!!!!!!!!!!!!! Corrupt images found !!!!!!!!!!!!!!!!!')
else:
    print('\n\nNo corrupt images')

print('\n\nPress enter to close')
input()






