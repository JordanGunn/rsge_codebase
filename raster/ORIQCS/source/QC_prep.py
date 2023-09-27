import os
import glob
import random
import shutil
import subprocess
import concurrent.futures

from tkinter import Tk
from tqdm import tqdm
from tkinter.filedialog import askdirectory
from Create_COG import CloudOptimizedGeotiff


# test locations

#qc_dest = R'D:\test'
#idir_o = R"F:\ndmp_2019\imagery\3band_orthophotography\tiff"
#idir_l = R"D:\Projects\2019\NDMP_2019"
#odir = R"D:\test\prepare_ortho"

def get_sample_images(tifList, sample):
    
    '''
    extensions= ("*.tif", "*.tiff")
    tifList = []
    for extension in extensions:
        tifList.extend(glob.glob(idir+"/"+extension)) 
                             # Create list of rasters
    '''
    """Generate random sample of rasters for QC"""
    sample_size = int(len(tifList)*sample)                                 # define total sample size
    sample_set = set({})                                                    # create empty set
    while len(sample_set) < sample_size:                                    # while set is smaller than sample size add random samples index values
        i = random.randrange(0, len(tifList))                              # generate random numbers
        sample_set.add(i)                                                   # add random number index values to set
    sample_set = list(sample_set)                                           # convert to list
    sample_set.sort()                                                       # sort list
    sample_files = []                                                       # create empty list
    for x in sample_set:                                                    # for all random integer index values in set
        sample_files.append(tifList[x])                                    # index tif list to get random selection of rasters
    #print("Sample_files: ", sample_files)
    return sample_files

def copy_raster_samples(list, odir):
    """Copy raster sample set to new directory for convenience"""

    dest = os.path.join(odir, 'raster_samples')              # staging area directory for uncompressed raster samples
    if not os.path.exists(dest):                            # if directory doesn't exist
        os.mkdir(dest)                                      # make new directory to copy raster samples
    for f in list:                                    # for files in sample list
        # if os.path.isfile(f):                               # make sure file is not folder
            # if not os.path.exists(os.path.join(dest, f)):   # if the file doesn't exist already
        shutil.copy(f, dest)                        # copy to out directory


def compress_samples(odir, cores):

    """Compress, internally tile, and generate overviews for raster qc samples"""
    
    dest = os.path.join(odir, 'compressed_raster_samples')   # destination for compressed samples
    if not os.path.exists(dest):                            # if directory doesn't exist
        os.mkdir(dest)                                      # make destination directory
    raster_dir = os.path.join(odir, 'raster_samples')         # location of intitial samples 
    extensions= (".tif", ".tiff")
    tifList = []
    for extension in extensions:
        tifList.extend(glob.glob(raster_dir+"/*"+extension))                               # list of samples          
    obj = CloudOptimizedGeotiff()                                                          # initialize class
    obj.overview_levels = 2, 4, 8, 16                                                      # specify levels of overviews
    obj.compress_method = 'JPEG'                                                           # set compression method to JPEG
    with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:            # compress and internally tile sample rasters
            [executor.submit(obj.compress_and_tile, [file, dest]) for file in tifList]                 
    obj.batch_create_overviews(dest)                                                       # create overviews for samples
    #obj.remove_intermediate_tif(raster_dir)                                                # remove initial samples


def write_raster_list(list, odir):

    """Write sample rasters to a text file for records"""

    with open(os.path.join(odir, 'raster_sample_list.txt'), 'w+') as f:  # create new text file
        for l in list:                                                  # for files in list      
            x = l.split('\\')                                           # split by path seperator
            f.write(f'{x[-1]}\n')                                       # write last index value of seperated path to text file


def write_lidar_list(list, odir):

    """Write sample lidar files to a text file"""

    with open(os.path.join(odir, 'lidar_sample_list.txt'), 'a+') as f:  # create new text file
        for l in list:                                                  # for files in list
            f.write(f'{l}\n')                                           # write name of lidar files


def get_sample_lidar(sample_raster_list, idir_lidar, odir, recurse, verbose=False):
    
    """Find matching lidar tiles that overlap with raster samples"""
    
    samples = len(sample_raster_list)                                            # get number of samples for reporting
    lidar_samples = []                                                          # empty list for appending
    extensions= ("*.las", "*.laz")
    laz_list = []                                                               # get list of laz files in absolute parent directory
    for extension in extensions:
        if recurse == 1:
            laz_list.extend(glob.glob(idir_lidar+"/"+extension), recursive=True)
        else:
            laz_list.extend(glob.glob(idir_lidar+"/"+extension))
    file_list = [f for f in laz_list if 'bc' in f and 'bcts' not in f]          # remove raw laz files by checking name (full file name list)
    file_list.sort()                                                            # sort the list
    base_file_list = []
    for f in file_list:
        base_file_list.append(f.split('\\')[-1][0:16])                          # sort the list                                              
    while len(sample_raster_list) > 0:                                           # while the list has items in it
        for f in sample_raster_list:                                             # for each raster sample
            tile = f.split('\\')[-1][0:16]                                      # get tile name from sample raster list                                   
            i = binary_search(base_file_list, 0, len(base_file_list)-1, tile)   # get index value of matching tile from laz files
            if i != -1:                                                         # if matching lidar tile exists
                lidar_samples.append(file_list[i])                              # append lidar samples with lidar file
            sample_raster_list.remove(f)                                         # remove raster sample from list
    if verbose:
        print(f'{len(lidar_samples)} matching lidar tiles found for {samples} rasters ({int((len(lidar_samples)/samples)*100)}%)')
    
    return lidar_samples


def binary_search(list, l, r, x):

    """Binary search recursive function"""
    
    if r >= l:                                          # check the base case
        mid = l + (r - l) // 2                          # get middle of the list
        if list[mid] == x:                              # check if element is middle of the list
            return mid
        elif list[mid] > x:                             # if middle value is larger than element check left side
            return binary_search(list, l, mid-1, x)     # recursively call search again on left side of list
        else:
            return binary_search(list, mid+1, r, x)     # if not left side, then recursively check right 
    else:
        return -1                                       # else return false


def make_intensity_grid(lidar_sample_list, odir):
    
    """Function to create lidar intensity raster from lidar data overlapping raster samples"""
    
    # call LAStools to make intensity raster
    os.environ["PATH"] += os.pathsep + "C:\\LAStools\\bin"                              
    subprocess.call("lasgrid -lof " + os.path.join(odir, "lidar_sample_list.txt") + \
                    " -intensity -step 1 -average -gray -ocut 4 -odir " + odir + " -otif -cores 4")


def main():
    
    # set up directories using dialog
    Tk().withdraw()                                                     # close empty tkinter window that opens by default
    idir_raster = askdirectory(title='Select input raster directory')     # prompt for directory with target rasters
    idir_lidar = askdirectory(title='Select input lidar directory')     # prompt for directory with lidar data
    odir = askdirectory(title='Select output directory')                # prompt for target output directory

    # run functions
    raster_list = get_sample_images(idir_raster, .25)                     # get random sample of dataset
    write_raster_list(raster_list, odir)                                  # make a list of files in sample for records
    copy_raster_samples(raster_list, odir)                                # copy samples to new location for convenience
    compress_samples(odir, 4)                                              # compress, tile, and create overviews
    # os.remove(os.path.join(odir, 'raster_samples'))                    # remove staging area directory for uncompressed raster samples
    if os.path.exists(idir_lidar):
        lidar_list = get_sample_lidar(raster_list, idir_lidar)           # find any overlapping lidar data
        write_lidar_list(lidar_list, odir)                              # write list of overlapping lidar data to text file
        make_intensity_grid(lidar_list, odir)                           # make intensity raster from overlapping lidar data

def run_from_gui(tifList, odir, idir_lidar, recurse, cores, sampleSize):
    
    odir += '/QC_Prep'
    if not os.path.exists(odir):
        os.makedirs(odir)
    # run functions
    raster_list = get_sample_images(tifList, sampleSize)                     # get random sample of dataset
    write_raster_list(raster_list, odir)                                  # make a list of files in sample for records
    copy_raster_samples(raster_list, odir)                                # copy samples to new location for convenience
    #compress_samples(odir, cores)                                              # compress, tile, and create overviews
    # os.remove(os.path.join(odir, 'raster_samples'))                    # remove staging area directory for uncompressed raster samples
    if idir_lidar != None:

        lidar_list = get_sample_lidar(raster_list, idir_lidar, odir, recurse)               # find any overlapping lidar data
        write_lidar_list(lidar_list, odir)                                  # write list of overlapping lidar data to text file
        make_intensity_grid(lidar_list, odir)                               # make intensity raster from overlapping lidar data


if __name__ == "__main__":
    main()