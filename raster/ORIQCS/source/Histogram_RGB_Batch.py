from osgeo import gdal

import os

import csv
import matplotlib.pyplot as plt
import glob
import pandas as pd
import concurrent.futures

from PIL import Image
from PyPDF2 import PdfFileMerger, PdfFileReader


def run_from_gui(indir, output, flist, recurse, cores):
    # allow gdal to handle runtime errors
    gdal.UseExceptions()

    plt.rcParams["figure.figsize"] = 10, 6

    output += '/Histogram_RGB/'

    if not os.path.exists(output):
        os.makedirs(output)
    '''
    extensions= ("*.tif", "*.tiff")
    flist = []
    for extension in extensions:
        flist.extend(glob.glob(indir+"/"+extension))
    '''
    pngFiles = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:

        try:
            results = [executor.submit(run_info, [file, output, recurse]) for file in flist]
        except concurrent.futures.process.BrokenProcessPool or concurrent.futures.process._RemoteTraceback:
            print("PPE ERROR CAUGHT!!!!!!!!!!!!!", flush=True)

        for f in concurrent.futures.as_completed(results):
            try:
                result = f.result()
                pngFiles.append(result)
            except Exception as e:
                print(f'Exception: {e}')

    for i in pngFiles:
        #fn = os.path.splitext(os.path.basename(i))[0]
        rgba = Image.open(i).convert('RGBA')
        rgb = Image.new('RGB', rgba.size, (255,255,255))
        rgb.paste(rgba, mask=rgba.split()[3])
        rgb.save(output + os.path.basename(i) + ".pdf", 'PDF', resoultion=100.0)
        pdf = output + os.path.basename(i) + ".pdf"
        pdfFN = os.path.join(output, "All_Histograms.pdf")
        merger = PdfFileMerger()
        if os.path.isfile(pdfFN):
            merger.append(PdfFileReader(pdfFN), "rb")
        merger.append(pdf)
        merger.write(pdfFN)
        merger.close()
        os.remove(pdf)
        os.remove(i)

    # Delete GDAL xml files
    for f in glob.glob(os.path.join(indir, '*.xml')):
        os.remove(f)


def run_info(args):
    file, output, recurse = args
    outname = os.path.basename(file)
    try:

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
        plt.savefig(output + '/' + outname + '_hist.png')
        pngFile = (output + '/' + outname + '_hist.png')
        # plt.show()

        # Reset plot and close image
        plt.clf()
        im = None
    except RuntimeError:
        print('Unable to open ' + outname)
        if recurse == 1:
            y = file, 'Error opening file'
        else:
            y = outname, 'Error opening file'
        with open(output + '/image_errors.csv', 'a') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', dialect='excel')
            wr.writerow(y)
    return pngFile

'''
def run_from_gui(indir, output):
    # allow gdal to handle runtime errors
    gdal.UseExceptions()

    plt.rcParams["figure.figsize"] = 10,6
    #Tk().withdraw()
    #indir = filedialog.askdirectory(title = 'Select input image directory')
    #output = filedialog.askdirectory(title = 'Select directory for histogram output')
    output += '/Histogram_RGB/'
    
    if not os.path.exists(output):
        os.makedirs(output)
    
    pngFiles = run_info(indir, output)
    #print(f'{pngFiles=}')
    
    for i in pngFiles:
        #fn = os.path.splitext(os.path.basename(i))[0]
        rgba = Image.open(i).convert('RGBA')
        rgb = Image.new('RGB', rgba.size, (255,255,255))
        rgb.paste(rgba, mask=rgba.split()[3])
        rgb.save(output + os.path.basename(i) + ".pdf", 'PDF', resoultion=100.0)
        pdf = output + os.path.basename(i) + ".pdf"
        pdfFN = os.path.join(output, "All_Histograms.pdf")
        merger = PdfFileMerger()
        if os.path.isfile(pdfFN):
            merger.append(PdfFileReader(pdfFN), "rb")
        merger.append(pdf)
        merger.write(pdfFN)
        merger.close()
        os.remove(pdf)
        os.remove(i)
        
    # Delete GDAL xml files
    for f in glob.glob(os.path.join(indir, '*.xml')):
        os.remove(f)
    #print('Done!')

def run_info(indir, output):
    
    extensions= ("*.tif", "*.tiff")
    flist = []
    for extension in extensions:
        flist.extend(glob.glob(indir+"/"+extension))
    
    s = 0
    total = len(flist)
    pngFiles = []
    for file in flist:
        outname = os.path.basename(file)
        try:
            # Print progress
            s += 1
            # print('Processing', s, 'of', total)
            print(f'Processing {s} of {total} -- {outname}', flush=True)

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
            pngFiles.append(output + '/' + outname+'_hist.png')
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
    return pngFiles
'''