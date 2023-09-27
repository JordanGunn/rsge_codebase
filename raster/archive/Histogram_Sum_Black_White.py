import gdal
import sys
import os
import numpy as np
import glob2
import csv
import time


#### PLACE IN FOLDER WITH TIF IMAGES AND RUN


start_time = time.time()

# allow gdal to handle runtime errors
gdal.UseExceptions()

# set thresholds for black and white
BL = 0.005
WH = 0.002

# create list of files and progress tracker
list = glob2.glob('**\*.tif')
s = 0
total = len(list)

for file in list:
    try:
        s += 1
        print('Checking', s, 'of', total)
        # open file
        im = gdal.Open(file)

        # read individual rgb bands as arrays
        rBand = im.GetRasterBand(1).ReadAsArray()
        gBand = im.GetRasterBand(2).ReadAsArray()
        bBand = im.GetRasterBand(3).ReadAsArray()

        # get image info
        cols = im.RasterXSize
        rows = im.RasterYSize
        pixels = cols * rows
        # print(pixels)

        # add bands together
        band_sum = rBand.astype(np.uint16) + gBand + bBand
        # band_sum = np.add(rBand,gBand,bBand, dtype=np.uint64)
        # print(band_sum)

        # create histogram data
        bins = np.linspace(0, 765, num=766)
        histo = np.histogram(band_sum, bins=bins)
        x = histo[0]

        # calculate percentage of black and white pixels in image
        # black = x[0] / pixels
        # white = x[764] / pixels
        black = sum(x[:20]) / pixels
        white = sum(x[745:]) / pixels

        if black > BL or white > WH:
            y = [file]
            if black > BL:
                    y.append('Black pixels')
                    y.append(black)
            if white > WH:
                    y.append('White pixels')
                    y.append(white)
            with open('black_white_checks.csv', 'a', newline='') as csvfile:
                wr = csv.writer(csvfile, delimiter=',', dialect='excel')
                wr.writerow(y)
        im = None
    except RuntimeError:
        print('Unable to open ' + file)
        y = file, 'Error opening file'
        # print x
        # sys.exit(1)
        with open('black_white_checks.csv', 'a') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', dialect='excel')
            wr.writerow(y)

print("--- %s seconds ---" % (time.time() - start_time))
# print(len(list), 'files')