from gdalnumeric import BandWriteArray, BandReadAsArray, CopyDatasetInfo
from laspy.file import File
from math import floor,ceil
from tqdm import tqdm

from tkinter import filedialog
from tkinter import Tk

import pandas as pd
import numpy as np

import sys
import os

import gdal
import osr

import glob


class Grid:
    """Class to generate density and/or intensity grids from lidar."""
    def __init__(self):
        self.path = None #
        self.file_object = None #
        self.array = None
        self.cell_size = 1 #
        self.row = None #
        self.col = None #
        self.NoDATA = None
        self.crs = None #
        self.min = None
        self.max = None
        self.verbose = False

    # create dictionary to assign projection from filename (All projections wrt to NAD83 (CSRS))
        self.proj_dict = {
            'utm08': 3155, 
            'utm8': 3155,
            'utm09': 3156,
            'utm9': 3156,
            'utm10': 3157,
            'utm11': 2955,
            'bcalb': 3005
            }


    def read_lidar(self, filepath, outdir):
        """Method for reading las or laz data with error handling."""
        # handle laz file if it is encountered
        # Open las/laz file in read mode

        self.path = filepath

        if 'laz' in os.path.splitext(filepath)[1]:
            os.environ["PATH"] += os.pathsep + 'C:\\LAStools\\bin'
            if self.verbose:
                print('\nDecompressing LAZ file...\n')
            try:
                self.file_object = File(filepath, mode='r')
                if self.verbose:
                    print('Finished decompressing')
            except Exception as e:
                print(f'Error opening {filepath}, file may be corrupt...\n')
                with open(f"{outdir}\\lidar_read_errors.txt", mode='a+') as f:
                    f.write(f"{filepath}: {e}\n")
        else:
            try:
                self.file_object = File(filepath, mode='r')
            except Exception as e:
                print(f'Error opening {filepath}, file may be corrupt...\n')
                with open(f"{outdir}\\lidar_read_errors.txt", mode='a+') as f:
                    f.write(f"{filepath}: {e}\n")
        if self.verbose:
            print(f'Created laspy file object from {filepath}')
        return self.file_object


    def proj_from_epsg(self, EPSG_code):
        """Method to generate OGC wkt georeferencing metadata from EPSG code."""

        self.crs = None
        sr = osr.SpatialReference() # Setup georeferencing info
        sr.ImportFromEPSG(EPSG_code)  # pass in the epsg code
        self.crs = sr.ExportToWkt()  # export georeferencing metadata in Well-Known Text format
        return self.crs


    def epsg_from_name(self, file):
        str_str = os.path.splitext(os.path.basename(file))[0].split('_')  # split filename by underscore
        for ind, s in enumerate(str_str):
            try:
                if 'utm' in s or 'bcalb' in s: # check for proj in filename
                    proj = str_str[ind]  # use index value to get proj from split string np.array
                    self.epsg = self.proj_dict[proj]  # use index value as key to get value from dictionary
                    return self.epsg
            except:
                wrong_fname = open('wrong_filename.txt', 'a+')  # creat file to log incorrectly named files
                wrong_fname.write(os.path.basename(file) + '\n')  # write the filename to the text file
                wrong_fname.close()  # close the file


    def create_density_grid(self, last_return=False, filter_by_class=None):
        """
        Method to create density grid from lidar. User must have grid.file_object attribute
        set first using the read_lidar method. User can filter by last return or class code.

        filter by keyword argument parameters, either filter by class, last return, both, or neither
        then extract x, y, z values from file to be used later for density calculations
        """
        self.NoDATA = 0  # !!!!!!!!!!!!!!! Changed from -1 to 0 on 2019-08-13 !!!!!!!!!!!!!!!!
        self.array = None
        self.grid_type = 'density'

        # extract minimum and maximum from input file; floor min & ceiling max
        las = self.file_object
        self.min = [floor(las.header.min[0]), floor(las.header.min[1])]
        # self.max = [ceil(las.header.max[0]), ceil(las.header.max[1])]
        self.max = [floor(las.header.max[0])+1, floor(las.header.max[1])+1]

        # get x and axis distance (m) from las file
        dist_x = self.max[0] - self.min[0]
        dist_y = self.max[1] - self.min[1]
        # calculate number of columns for raster grid
        self.col = int(dist_x/self.cell_size)
        # self.col += 1
        self.row = int(dist_y/self.cell_size)
        # self.row += 1

        if last_return and filter_by_class is None:
            las_return_x, las_return_y = (
                las.x[las.num_returns == las.return_num],
                las.y[las.num_returns == las.return_num]
                )
            return_filter = True
            class_filter = False
            filter_filter = False

        elif filter_by_class is not None and last_return is False:
            las_class_x, las_class_y = (
                las.x[las.Classification == filter_by_class],
                las.y[las.Classification == filter_by_class]
                )
            class_filter = True
            return_filter = False
            filter_filter = False

        elif filter_by_class is not None and last_return:
            las_filter_x, las_filter_y = (
                las.x[las.Classification == filter_by_class
                      and las.num_returns == las.return_num],
                las.y[las.Classification == filter_by_class
                      and las.num_returns == las.return_num]
                )
            filter_filter = True
            class_filter = False
            return_filter = False

        else:
            las_x, las_y = las.x, las.y
            class_filter = False
            return_filter = False
            filter_filter = False

        # Create empty numpy array to write values to
        count = np.zeros((self.row, self.col)).astype(np.int8)

        # Apply -1 to have negative y resolution for raster
        ycell = -1 * self.cell_size

        # Scale or "project" values  of lidar data to grid,
        if return_filter:
            scale_x = (las_return_x - self.min[0]) / self.cell_size
            scale_y = (las_return_y - self.min[1]) / ycell

        elif class_filter:
            scale_x = (las_class_x - self.min[0]) / self.cell_size
            scale_y = (las_class_y - self.min[1]) / ycell

        elif filter_filter:
            scale_x = (las_filter_x - self.min[0]) / self.cell_size
            scale_y = (las_filter_y - self.min[1]) / ycell
        else:
            scale_x = (las_x - self.min[0]) / self.cell_size
            scale_y = (las_y - self.min[1]) / ycell

        # change type to integer and save as variables to use for index values
        ind_x = scale_x.astype(np.int8)
        ind_y = scale_y.astype(np.int8)

        # Loop through lidar point records, count, and add to raster grid
        if self.verbose:
            print(f'\nCalculating density for {os.path.splitext(os.path.basename(self.path))[0]}...')

        # Runtime bottleneck - This is O(n) WRT the number of points in the point cloud
        # We can't do better than this withouth sacrificing accuracy
        for x, y in np.nditer([ind_x, ind_y]):
            count[y, x] += 1

        np.savetxt('D:\\count.txt', count)
        # Fill areas areas lacking data with keyword argument specified no data value
        count_noData = (np.where(count > 0, count, self.NoDATA)).astype(np.int8)

        # calculate density
        self.array = (count_noData / self.cell_size).astype(np.int8)
        # lazy fix for top row of cells being generated outside AOI inexplicably
        self.array = np.delete(self.array, 0, axis=0)
        return self.array


    def create_intensity_grid(self):
        """
        Method to create intensity grid from lidar. User must have grid.file_object attribute
        set first using the read_lidar method.
        """
        self.NoDATA = 0
        self.array = None
        self.grid_type = 'intensity'
        las = self.file_object

        # extract minimum and maximum from input file
        self.min = [floor(las.header.min[0]), floor(las.header.min[1])]
        # self.max = [ceil(las.header.max[0]), ceil(las.header.max[1])]
        self.max = [floor(las.header.max[0])+1, floor(las.header.max[1])+1]

        # extract x, y values from file to be used later for density calculations
        las_x, las_y, las_i = las.x, las.y, las.intensity

        # get x axis distance (m) from las file
        dist_x = self.max[0] - self.min[0]

        # get y axis distance (m) from las file
        dist_y = self.max[1] - self.min[1]

        # calculate number of columns for raster grid
        self.col = int(dist_x/self.cell_size)
        # self.col += 1  # add one to avoid rounding issues

        # Apply -1 to have negative y resolution for raster
        ycell = -1 * self.cell_size

        # calculate number of rows for raster grid
        self.row = int(dist_y/self.cell_size)
        # self.row += 1  # add one to avoid rounding issues

        # Create empty numpy array to write values to
        count = np.zeros((self.row, self.col)).astype(np.int32)

        # Aggregate intensity values
        int_sum = np.zeros((self.row, self.col)).astype(np.int32)

        # Scale or "project" values  of lidar data to grid,
        scale_x = (las_x - self.min[0]) / self.cell_size
        scale_y = (las_y - self.min[1]) / ycell

        # change type to integer and save as variables to use for index values
        ind_x = scale_x.astype(np.int32)
        ind_y = scale_y.astype(np.int32)

        # Loop through lidar point records, count, and add to raster grid
        if self.verbose:
            print(f'\nCalculating intensity for {os.path.splitext(os.path.basename(self.path))[0]}...')

        # Runtime bottleneck - This is O(n) WRT the number of points in the point cloud
        # We can't do better than this withouth sacrificing accuracy
        for x, y, i in np.nditer([ind_x, ind_y, las_i]):
            count[y, x] += 1
            int_sum[y, x] += i

        # Fill areas areas lacking data with 1 to avoid divide by zero error
        count_noZero = (np.where(count > 0, count, 1)).astype(np.int32)

        # calculate intensity
        int_avg = (int_sum / count_noZero).astype(np.int32)

        # scale intensity grid to 8bit unsigned integers
        # int_scaled = (int_avg / 256).astype(np.int32)

        # Interpolate 0 values in array to avoid any holes in data
        self.array = np.where(np.logical_and(int_avg > 1, int_avg != 0),
                              int_avg, self.NoDATA).astype(np.int32)

        self.array = np.delete(self.array, 0, axis=0)
        # lazy fix for top row of cells being generated outside AOI inexplicably


    def save_grid(self, gridtype='unspecified', outdir=None, output_format='tif'):
        """Method to save grid to output in either Geotiff or ESRI ASCII format"""
        tgt = f'{outdir}\\{os.path.splitext(os.path.basename(self.path))[0]}_{gridtype}_grid.{output_format}'
        grid = self.array

        if output_format == 'asc':
            # Create ASCII header
            header = "ncols {}\n".format(grid.shape[1])
            header += "nrows {}\n".format(grid.shape[0])
            header += "xllcorner {}\n".format(floor(self.min[0]))
            header += "yllcorner {}\n".format(ceil(self.min[1]))
            header += "cellsize {}\n".format(self.cell_size)
            header += "NODATA_value {}\n".format(self.NoDATA)

            # Open output file, write header, save array to output file
            if grid is not None:
                with open(tgt, "wb") as f:
                    f.write(bytes(header, 'UTF-8'))
                    # fmt string to output integers only
                    np.savetxt(f, grid, fmt="%.0f")
            else:
                raise Exception('No array attribute found for grid object')

        elif output_format == 'tif':
            # create new raster and write array to image
            driver = gdal.GetDriverByName('GTiff')  # get geotiff driver
            if grid is not None:
                out_img = driver.Create( # create raster object
                    tgt, self.col, self.row, 1, gdal.GDT_UInt16,
                    options=['COMPRESS=LZW', 'NUM_THREADS=ALL_CPUS'])
                out_img.SetGeoTransform(( # set positional parameters
                    floor(self.min[0]), self.cell_size, 0,
                    ceil(self.max[1]), 0, self.cell_size*-1))
                out_band = out_img.GetRasterBand(1) # get band from raster object
                out_band.SetNoDataValue(self.NoDATA)
                out_band.WriteArray(grid) # write array to raster band
                # write wkt proj metadata to image if it exists
                if self.crs is not None:
                    out_img.SetProjection(self.crs)
                out_band.FlushCache()
                out_band = None
                out_img = None
            else:
                raise Exception('No array attribute found for grid object')


def main():
    
    Tk().withdraw()

    # Specify input and output directory
    indir = filedialog.askdirectory(title='Select input directory')
    output = filedialog.askdirectory(title='Select directory for shapefile output')

    # Change directory to output location
    os.chdir(output)

    # gather list of all las or laz files in directories and sub-directories and report number of files
    las_list = glob.glob(os.path.join(indir, '**/*.las'), recursive=True)
    laz_list = glob.glob(os.path.join(indir, '**/*.laz'), recursive=True)
    las_list.extend(laz_list)
    print('\n\n' + str(len(las_list)) + ' lidar files found')
    
    # instantiate class
    grid = Grid()

    # request user input for grid types
    gd = input("Would you like to create ground density grids for the given directory? (y/n):\t")
    lrd = input("\nWould you like to create last return density grids for the given directory? (y/n):\t")
    i = input("\nWould you like to create intensity grids for the given directory? (y/n):\t")

    if gd == 'n' and lrd == 'n'and i == 'n':
        print('Exiting')
        sys.exit()

    if gd == 'y' or gd == 'Y':    
        # loop through files and create grids
        print('Creating ground density grids...')
        for f in tqdm(las_list):
            grid.read_lidar(f, output)
            epsg = grid.epsg_from_name(os.path.basename(f))
            grid.proj_from_epsg(epsg)
            grid.create_density_grid(filter_by_class=2)
            grid.save_grid(outdir=output, gridtype='ground_density')

    if lrd == 'y' or lrd == 'Y':    
        # loop through files and create grids
        print('Creating last return density grids...')
        for f in tqdm(las_list):
            grid.read_lidar(f, output)
            epsg = grid.epsg_from_name(os.path.basename(f))
            grid.proj_from_epsg(epsg)
            grid.create_density_grid(last_return=True)
            grid.save_grid(outdir=output, gridtype='last_density')

    if i == 'y' or i == 'Y':
        # loop through files and create grids
        print('Creating intensity grids...')
        for f in tqdm(las_list):
            grid.read_lidar(f, output)
            epsg = grid.epsg_from_name(os.path.basename(f))
            grid.proj_from_epsg(epsg)
            grid.create_intensity_grid()
            grid.save_grid(outdir=output, gridtype='intensity')

if __name__ == '__main__':
    main()




