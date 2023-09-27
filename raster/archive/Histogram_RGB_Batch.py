import gdal
import os
import csv
import matplotlib.pyplot as plt
import glob
import pandas as pd
from tkinter import filedialog
from tkinter import Tk


# allow gdal to handle runtime errors
gdal.UseExceptions()


plt.rcParams["figure.figsize"] = 10,6
Tk().withdraw()
indir = filedialog.askdirectory(title = 'Select input image directory')
output = filedialog.askdirectory(title = 'Select directory for histogram output')

list = glob.glob(os.path.join(indir, '**/*tif'), recursive=True)
s = 0
total = len(list)

for file in list:
    outname = os.path.basename(file)
    try:
        # Print progress
        s += 1
        # print('Processing', s, 'of', total)
        print(f'Processing {s} of {total} -- {outname}')

        # Open image file
        im = gdal.Open(file)

        # Get individual band histograms
        rBand = im.GetRasterBand(1).GetHistogram(-0.5, 255.5, 256, False, False)
        gBand = im.GetRasterBand(2).GetHistogram(-0.5, 255.5, 256, False, False)
        bBand = im.GetRasterBand(3).GetHistogram(-0.5, 255.5, 256, False, False)
        # print rBand
        # print gBand
        # print bBand

        # Create RGB histogram table, order columns and output table
        table = pd.DataFrame({'RED': rBand, 'GREEN': gBand, 'BLUE':bBand})
        column_order = ['RED', 'GREEN', 'BLUE']
        # print table
        table[column_order].to_csv(output + '/' + outname + '_histo.csv')


        # Plot histogram data
        plt.plot(rBand, 'tab:red')
        plt.plot(gBand, 'tab:green')
        plt.plot(bBand, 'tab:blue')

        # Format plot
        plt.xlabel('DN')
        plt.ylabel('Frequency')
        plt.title(outname)
        plt.rc('axes', axisbelow=True)
        plt.grid(linestyle='dotted')
        plt.ticklabel_format(style='plain')

        # Save histogram as a PNG
        plt.savefig(output + '/' + outname+'_hist.png')
        # plt.show()

        # Reset plot and close image
        plt.clf()
        im = None
    except RuntimeError:
        print('Unable to open ' + outname)
        y = outname, 'Error opening file'
        with open(output + '/image_errors.csv', 'a') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', dialect='excel')
            wr.writerow(y)

# Delete GDAL xml files
for f in glob.glob(os.path.join(indir, '*.xml')):
    os.remove(f)
print('Done!')

