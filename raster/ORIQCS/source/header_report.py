import os
import csv
import glob

from osgeo import gdal
import concurrent.futures
from tkinter import Tk
from functools import partial


class HeaderReport:
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
    > Reserved (in lieu of future recommendations)
    > Reserved (in lieu of future recommendations)
    > Reserved (in lieu of future recommendations)
    > Reserved (in lieu of future recommendations)

    Written by: Jordan Godau
    """

    # enable gdal to use python exceptions
    gdal.UseExceptions()

    def __init__(self, image_file):
        """
        Initialize class by reading in an image
        and assigning attributes
        """
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
        self.image_dict['RASTER SIZE (X, Y)'] = clean_string(str(self.size))  # add to the iamge dictionary, clean the results

        # Record the band count ----->
        self.image_dict['BAND COUNT'] = self.image_file.RasterCount  # get the band count attribute from the raster, add to dictionary

    def band_info(self):
        """
        Method to loop through multiple bands
        and collect information about each band
        """
        # Set up empty dictionaries
        self.band_mean = {}
        self.band_colors = {}
        self.band_nodata = {}
        self.band_minmax = {}
        self.band_datatypes = {}
        self.band_overview_count = {}

        # Loop through image bands and collect information
        for band_num in range(1, self.image_file.RasterCount+1):
            
            # Get raster band
            band = self.image_file.GetRasterBand(band_num)

            # Compute statistics for the band
            band.ComputeStatistics(0)

            # Assign metadata dictionary to variable
            # (band statistics are written as a metadata entry)
            stat_dict = band.GetMetadata()

            # Get band color
            self.band_colors[f'band{str(band_num)}'] = gdal.GetColorInterpretationName(
                band.GetColorInterpretation()
            )

            # Get band datatype
            self.band_datatypes[f'band{str(band_num)}'] = gdal.GetDataTypeName(band.DataType)

            # Get band no data value
            self.band_nodata[f'band{str(band_num)}'] = band.GetNoDataValue()

            # Get band min and max
            self.band_minmax[f'band{str(band_num)}'] = (
                stat_dict['STATISTICS_MINIMUM'],
                stat_dict['STATISTICS_MAXIMUM']
            )

            # Get band mean
            self.band_mean[f'band{str(band_num)}'] = stat_dict['STATISTICS_MEAN']

            # Get the overview count
            self.band_overview_count[f'band{str(band_num)}'] = band.GetOverviewCount()

            # Write band colors to the image dictionary
            if len(self.band_colors.values()) == 1:
                # Add if only one value
                self.image_dict[
                    f'BAND COLORS (BANDS 1 - {self.image_file.RasterCount})'
                ] = list(self.band_colors.values())[0]
            else:
                # Convert to string and clean if multiple values
                self.image_dict[
                    f'BAND COLORS (BANDS 1 - {self.image_file.RasterCount})'
                ] = clean_string(str(tuple(self.band_colors.values())))

            # Write band datatype to the image dictionary
            if len(self.band_datatypes.values()) == 1:
                # Add if only one value
                self.image_dict[
                    f'DATA TYPE (BANDS 1 - {self.image_file.RasterCount})'
                ] = list(self.band_datatypes.values())[0]
            else:
                # Convert to string and clean if multiple values
                self.image_dict[
                    f'DATA TYPE (BANDS 1 - {self.image_file.RasterCount})'
                ] = clean_string(str(tuple(self.band_datatypes.values())))

            # Write band no data values to the image dictionary
            if len(self.band_nodata.values()) == 1:
                # Add if only one value
                self.image_dict[
                    f'NO DATA VALUE (BANDS 1 - {self.image_file.RasterCount})'
                ] = list(self.band_nodata.values())[0]
            else:
                # Convert to string and clean if multiple values
                self.image_dict[
                    f'NO DATA VALUE (BANDS 1 - {self.image_file.RasterCount})'
                ] = clean_string(str(tuple(self.band_nodata.values())))

            # Write band overview count to the image dictionary
            if len(self.band_overview_count.values()) == 1:
                # Add if only one value
                self.image_dict[
                    f'OVERVIEW COUNT (BANDS 1 - {self.image_file.RasterCount})'
                ] = list(self.band_overview_count.values())[0]
            else:
                # Convert to string and clean if multiple values
                self.image_dict[
                    f'OVERVIEW COUNT (BANDS 1 - {self.image_file.RasterCount})'
                ] = clean_string(str(tuple(self.band_overview_count.values()))) 

        # Write min/max band values to the image dictionary
        for x, value in enumerate(self.band_minmax.values()):
            minmax_header = f'BAND {x + 1} MIN/MAX'
            self.image_dict[minmax_header] = clean_string(str(value))

        # Write mean band values to the image dictionary
        for x, value in enumerate(self.band_mean.values()):
            mean_header = f'BAND {x + 1} MEAN'
            self.image_dict[mean_header] = clean_string(str(value))

        return(self.image_dict)


'''
    def saveDict(self, full_image_dict, numOfFiles, out_name):
        for i in range(numOfFiles):
            full_image_dict.update(self.image_dict)
        output(full_image_dict, out_name)
'''


def clean_string(string):
    # clean string for output
    return string.replace('(', '').replace(')', '').replace("'", '')


def output(full_image_dict, out_name):
    """
    Write information to a CSV file.
    """
    # create the file and write the header
    if not os.path.exists(out_name): # if the file doesn't exist, make the file and write the header (this guarantess the header will only be written once)
        with open(out_name, 'a+', newline='') as csvfile:
            fieldnames = full_image_dict[0].keys()  # define fieldnames as dictionary keys
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # assign fieldnames as kwarg
            writer.writeheader() # write the header

    for i in range(len(full_image_dict)):
        # write information to the file
        with open(out_name, 'a', newline='') as csvfile:
            #for x in len(self.image_dict)
            fieldnames = full_image_dict[i].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(full_image_dict[i]) # write the entry into the summary file


def run_info(f, odir, recurse):
    # helper function to do all processing for each image
    # to be passed to executor for concurrency
    try:
        info = HeaderReport(f) # create HeaderReport instance
        result = info.band_info()  # run band info method
        #print(f'finished processing {f}')
        return result

    # if errors are encountered, write the error to a text file at the output location
    except Exception as e:  
        with open(os.path.join(odir, 'file_errors.txt'), 'a+') as p:
            if recurse == 0:
                p.write(f'{os.path.split(f)[1]}:\t{e}\n')
            else:
                p.write(f'{f}:\t{e}\n')


def run_from_gui(idir, odir, flist, recurse, cores):

    Tk().withdraw()  # close default empty tkinter window

    # prompt for input and output directory
    #idir = filedialog.askdirectory(title="Select input image directory")
    #odir = filedialog.askdirectory(title="Select output location")

    # !!! if new formats are needed, add them here as a wild card !!!
    '''
    extensions= ("*.tif", "*.tiff","*.asc", "*.dem")
    flist = []
    for extension in extensions:
        flist.extend(glob.glob(idir+"/"+extension))
    '''
    '''
    flist = [f for f in glob.glob(f'{idir}\\**\*',recursive=True)
                   if f[-4:] in {'.tif', '.asc', '.dem'}]
    '''
    # arg_pack = [(f, odir) for f in flist]
    '''
    for x in range(len(flist)):
        results = run_info(flist[x], odir)
        #print(results)

    '''
    run_info_part = partial(run_info, odir=odir, recurse=recurse)
    # results=[]
    full_image_dict={}
    for l in range(len(flist)):
        full_image_dict

    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
        x = executor.map(run_info_part, flist)
        # full_image_dict.update([i for i in x])
        i = 0
        for result in x:
            full_image_dict[i] = result
            i += 1

    #for f in executor.map(run_info_part, flist):
        #print(f'{f.result()=}')
    output(full_image_dict ,os.path.join(odir, 'header_report.csv'))
    #print(f'{full_image_dict}')
    '''
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # executor.map(run_info, arg_pack)
        results.append(executor.map(run_info_part, flist))
        
        #for r in results:
            #full_image_dict.update(r.result())
        for _ in concurrent.futures.as_completed(results):
            print('Result: ', _.result())
    '''
    # Delete GDAL xml files
    for f in glob.glob(os.path.join(idir, '*.xml')):
        os.remove(f)
    # for f in tqdm(flist):
    #     # run the code
    #     try:
    #         info = HeaderReport(f) # create HeaderReport instance
    #         info.band_info()  # run band info method
    #         info.output(os.path.join(odir, 'header_report.csv'))  # run output method
    #     # if errors are encountered, write the error to a text file at the output location
    #     except Exception as e:  
    #         with open(os.path.join(odir, 'file_errors.txt'), 'a+') as p:
    #             p.write(f'{f}:\t{e}\n')


#if __name__ == '__main__':
    #main()
