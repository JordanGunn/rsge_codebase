import os
import csv
import glob
import gdal
import concurrent.futures

from tqdm import tqdm
from tkinter import Tk
from functools import partial
from tkinter import filedialog


class ImageSummary:


    """
    This class generates a tabular imagery dataset summary from a directory of
    imagery data (such as tif format imagery).

    information summarized is as follows:

    > Filename
    > Projection
    > Raster size (x, y)
    > Pixel size (x, y)
    > Origin (x, y)
    > Band count
    > Band color interpretations
    > Band datatype
    > Band no data values
    > Band min/max
    > Band mean
    > Band overview count
    > Reserved (in lieu of future reccomendations)
    > Reserved (in lieu of future reccomendations)
    > Reserved (in lieu of future reccomendations)
    > Reserved (in lieu of future reccomendations)

    Written by: Jordan Godau
    """

    # enable gdal to use python exceptions
    gdal.UseExceptions()

    def __init__(self, image_file):

        """Initialize class by reading in an image and assigning attributes"""

        self.image_dict = {}  # create empty image dictionary to store metadata

        self.image_file = gdal.Open(image_file, gdal.GA_ReadOnly)  # open the image file
        
        # Record the filename ----->
        self.file_path = self.image_file.GetDescription()  # Get description (ie file path, {why would you call this description?!})
        file_split = self.file_path.split('\\')  # split full path by backslash character
        self.image_dict['FILENAME'] = file_split[-1]  # get the the last index value of the split string
        
        # Record the projection ----->
        self.srs = self.image_file.GetProjection()  # get the full spatial reference system
        proj_split = self.srs.split(',')  # split string by comma
        self.image_dict['PROJECTION'] = proj_split[0] + ']'  # take the first index value (location of the projection)
        if self.image_dict['PROJECTION'] == ']':
            self.image_dict['PROJECTION'] = 'None'

        # Record raster origin (x, y) ----->
        geotrans = self.image_file.GetGeoTransform()  # get geo transform parameters (origin {x, y} and pixel size {x, y})
        self.origin = (geotrans[0], geotrans[3])  # get origin values from geotransform tuple at index locations
        self.image_dict['ORIGIN (X, Y)'] = clean_string(str(self.origin))  # add to image dictionary, clean the results

        # Record pixel size (x, y) ----->
        self.pixel_size = (geotrans[1], geotrans[5])  # get pixel values from geotransform tuple at index locations
        self.image_dict['PIXEL SIZE (X, Y)'] = clean_string(str(self.pixel_size))  # add to image dictionary, clean the results

        # Record the image size in x and y ----->
        self.size = (self.image_file.RasterXSize, self.image_file.RasterYSize)  # get the image size attributes from the raster
        self.image_dict['IMAGE SIZE (X, Y)'] = clean_string(str(self.size))  # add to the iamge dictionary, clean the results

        # Record the band count ----->
        self.image_dict['BAND COUNT'] = self.image_file.RasterCount  # get the band count attribute from the raster, add to dictionary


    def band_info(self):

        """Method to loop through multiple bands and collect information about each band"""
        
        # set up empty dictionaries
        self.band_mean = {}
        self.band_colors = {}
        self.band_nodata = {}
        self.band_minmax = {}
        self.band_datatypes = {}
        self.band_overview_count = {}

        # loop through image bands and collect information
        for band_num in range(1, self.image_file.RasterCount+1):
            
            band = self.image_file.GetRasterBand(band_num)  # get raster band
            band.ComputeStatistics(0)  # compute statistics for the band
            stat_dict = band.GetMetadata()  #  assign metadata dictionary to variable (band statistics are written as a metadata entry)
            self.band_colors[f'band{str(band_num)}'] = gdal.GetColorInterpretationName(band.GetColorInterpretation())  # get band color
            self.band_datatypes[f'band{str(band_num)}'] = gdal.GetDataTypeName(band.DataType) # get band datatype
            self.band_nodata[f'band{str(band_num)}'] = band.GetNoDataValue()  # get band no data value
            self.band_minmax[f'band{str(band_num)}'] = (stat_dict['STATISTICS_MINIMUM'], stat_dict['STATISTICS_MAXIMUM'])  # get band min and max
            self.band_mean[f'band{str(band_num)}'] = stat_dict['STATISTICS_MEAN']  # get band mean
            self.band_overview_count[f'band{str(band_num)}'] = band.GetOverviewCount()  # get the overview count

            # write band colors to the image dictionary
            if len(self.band_colors.values()) == 1:
                self.image_dict[f'BAND COLORS (BANDS 1 - {self.image_file.RasterCount})'] = list(self.band_colors.values())[0]  # add if only one value
            else:
                self.image_dict[f'BAND COLORS (BANDS 1 - {self.image_file.RasterCount})'] = clean_string(str(tuple(self.band_colors.values())))  # convert to string and clean if multiple values

            # write band datatype to the image dictionary
            if len(self.band_datatypes.values()) == 1:
                self.image_dict[f'DATA TYPE (BANDS 1 - {self.image_file.RasterCount})'] = list(self.band_datatypes.values())[0]  # add if only one value
            else:
                self.image_dict[f'DATA TYPE (BANDS 1 - {self.image_file.RasterCount})'] = clean_string(str(tuple(self.band_datatypes.values())))  # convert to string and clean if multiple values

            # write band no data values to the image dictionary
            if len(self.band_nodata.values()) == 1:
                self.image_dict[f'NO DATA VALUE (BANDS 1 - {self.image_file.RasterCount})'] = list(self.band_nodata.values())[0]  # add if only one value
            else:
                self.image_dict[f'NO DATA VALUE (BANDS 1 - {self.image_file.RasterCount})'] = clean_string(str(tuple(self.band_nodata.values())))  # convert to string and clean if multiple values

            # write band overview count to the image dictionary
            if len(self.band_overview_count.values()) == 1:
                self.image_dict[f'OVERVIEW COUNT (BANDS 1 - {self.image_file.RasterCount})'] = list(self.band_overview_count.values())[0]  # add if only one value
            else:
                self.image_dict[f'OVERVIEW COUNT (BANDS 1 - {self.image_file.RasterCount})'] = clean_string(str(tuple(self.band_overview_count.values())))  # convert to string and clean if multiple values

        # write min/max band values to the image dictionary
        for x, value in enumerate(self.band_minmax.values()):
            minmax_header = f'BAND {x+1} MIN/MAX'
            self.image_dict[minmax_header] = clean_string(str(value))

        # write mean band values to the image dictionary
        for x, value in enumerate(self.band_mean.values()):
            mean_header = f'BAND {x+1} MEAN'
            self.image_dict[mean_header] = clean_string(str(value))


    def output(self, out_name):

        """Method to write information to a CSV file"""

        # create the file and write the header
        if not os.path.exists(out_name): # if the file doesn't exist, make the file and write the header (this guarantess the header will only be written once)
            with open(out_name, 'a+', newline='') as csvfile:
                fieldnames = self.image_dict.keys()  # define fieldnames as dictionary keys
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # assign fieldnames as kwarg
                writer.writeheader() # write the header

        # write information to the file
        with open(out_name, 'a', newline='') as csvfile:
            fieldnames = self.image_dict.keys() 
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(self.image_dict) # write the entry into the summary file


def clean_string(string):
    # clean string for output
    return string.replace('(', '').replace(')', '').replace("'", '')


def run_info(f, odir):
    # helper function to do all processing for each image
    # to be passed to executor for concurrency
    try:
        info = ImageSummary(f) # create ImageSummary instance
        info.band_info()  # run band info method
        info.output(os.path.join(odir, 'image_summary.csv'))  # run output method
        print(f'finished processing {f}')
    
    # if errors are encountered, write the error to a text file at the output location
    except Exception as e:  
        with open(os.path.join(odir, 'file_errors.txt'), 'a+') as p:
            p.write(f'{f}:\t{e}\n')


def main():
    
    Tk().withdraw()  # close default empty tkinter window

    # prompt for input and output directory
    idir = filedialog.askdirectory(title="Select input image directory")
    odir = filedialog.askdirectory(title="Select output location")
    
    # !!! if new formats are needed, add them here as a wild card !!!
    flist = [f for f in glob.glob(f'{idir}\\**\*',recursive=True)
                   if f[-4:] in {'.tif', '.asc', '.dem'}]

    # arg_pack = [(f, odir) for f in flist]
    run_info_part = partial(run_info, odir=odir)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # executor.map(run_info, arg_pack)
        executor.map(run_info_part, flist)

    # for f in tqdm(flist):
    #     # run the code
    #     try:
    #         info = ImageSummary(f) # create ImageSummary instance
    #         info.band_info()  # run band info method
    #         info.output(os.path.join(odir, 'image_summary.csv'))  # run output method
    #     # if errors are encountered, write the error to a text file at the output location
    #     except Exception as e:  
    #         with open(os.path.join(odir, 'file_errors.txt'), 'a+') as p:
    #             p.write(f'{f}:\t{e}\n')


if __name__ == '__main__':
    main()

