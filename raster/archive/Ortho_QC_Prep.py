import os
import glob
import random
import shutil
import subprocess

from tkinter import Tk
from tqdm import tqdm
from tkinter.filedialog import askdirectory
from Create_COG import CloudOptimizedGeotiff


# test locations
qc_dest = R'D:\test'
idir_o = R"F:\ndmp_2019\imagery\3band_orthophotography\tiff"
idir_l = R"D:\Projects\2019\NDMP_2019"
odir = R"D:\test\prepare_ortho"


def get_sample_images(idir, sample):
    
    """Generate random sample of ortho images for QC"""
    
    tif_list = glob.glob(os.path.join(idir,'**\*.tif'), recursive=True)     # Create list of orthos
    sample_size = int(len(tif_list)*sample)                                 # define total sample size
    sample_set = set({})                                                    # create empty set
    while len(sample_set) < sample_size:                                    # while set is smaller than sample size add random samples index values
        i = random.randrange(0, len(tif_list))                              # generate random numbers
        sample_set.add(i)                                                   # add random number index values to set
    sample_set = list(sample_set)                                           # convert to list
    sample_set.sort()                                                       # sort list
    sample_files = []                                                       # create empty list
    for x in sample_set:                                                    # for all random integer index values in set
        sample_files.append(tif_list[x])                                    # index tif list to get random selection of orthos

    return sample_files


def copy_ortho_samples(list, odir):
    
    """Copy ortho sample set to new directory for convenience"""

    dest = os.path.join(odir, 'ortho_samples')              # staging area directory for uncompressed ortho samples
    if not os.path.exists(dest):                            # if directory doesn't exist
        os.mkdir(dest)                                      # make new directory to copy ortho samples
    for f in tqdm(list):                                    # for files in sample list
        # if os.path.isfile(f):                               # make sure file is not folder
            # if not os.path.exists(os.path.join(dest, f)):   # if the file doesn't exist already
        shutil.copy(f, dest)                        # copy to out directory


def compress_samples(odir):

    """Compress, internally tile, and generate overviews for ortho qc samples"""
    
    dest = os.path.join(odir, 'compressed_ortho_samples')   # destination for compressed samples
    if not os.path.exists(dest):                            # if directory doesn't exist
        os.mkdir(dest)                                      # make destination directory
    ortho_dir = os.path.join(odir, 'ortho_samples')         # location of intitial samples 
    tif_list = glob.glob(ortho_dir + '\\*.tif')             # list of samples           
    obj = CloudOptimizedGeotiff()                           # initialize class
    obj.overview_levels = 2, 4, 8, 16                       # specify levels of overviews
    obj.compress_method = 'JPEG'                            # set compression method to JPEG
    obj.compress_and_tile(tif_list, dest)                   # compress and internally tile sample orthos
    obj.batch_create_overviews(dest)                        # create overviews for samples
    obj.remove_intermediate_tif(ortho_dir)                  # remove initial samples


def write_ortho_list(list, odir):

    """Write sample orthos to a text file for records"""

    with open(os.path.join(odir, 'ortho_sample_list.txt'), 'w+') as f:  # create new text file
        for l in list:                                                  # for files in list      
            x = l.split('\\')                                           # split by path seperator
            f.write(f'{x[-1]}\n')                                       # write last index value of seperated path to text file


def write_lidar_list(list, odir):

    """Write sample lidar files to a text file"""

    with open(os.path.join(odir, 'lidar_sample_list.txt'), 'a+') as f:  # create new text file
        for l in list:                                                  # for files in list
            f.write(f'{l}\n')                                           # write name of lidar files


def get_sample_lidar(sample_ortho_list, idir_lidar, verbose=False):
    
    """Find matching lidar tiles that overlap with ortho samples"""
    
    samples = len(sample_ortho_list)                                            # get number of samples for reporting
    lidar_samples = []                                                          # empty list for appending
    laz_list = glob.glob(os.path.join(idir_lidar, '**\*.laz'), recursive=True)  # get list of laz files in absolute parent directory
    file_list = [f for f in laz_list if 'bc' in f and 'bcts' not in f]          # remove raw laz files by checking name (full file name list)
    file_list.sort()                                                            # sort the list
    base_file_list = []
    for f in file_list:
        base_file_list.append(f.split('\\')[-1][0:16])                          # sort the list                                              
    while len(sample_ortho_list) > 0:                                           # while the list has items in it
        for f in sample_ortho_list:                                             # for each ortho sample
            tile = f.split('\\')[-1][0:16]                                      # get tile name from sample ortho list                                   
            i = binary_search(base_file_list, 0, len(base_file_list)-1, tile)   # get index value of matching tile from laz files
            if i != -1:                                                         # if matching lidar tile exists
                lidar_samples.append(file_list[i])                              # append lidar samples with lidar file
            sample_ortho_list.remove(f)                                         # remove ortho sample from list
    if verbose:
        print(f'{len(lidar_samples)} matching lidar tiles found for {samples} orthos ({int((len(lidar_samples)/samples)*100)}%)')
    
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
    
    """Function to create lidar intensity raster from lidar data overlapping ortho samples"""
    
    # call LAStools to make intensity raster
    os.environ["PATH"] += os.pathsep + "C:\\LAStools\\bin"                              
    subprocess.call("lasgrid -lof " + os.path.join(odir, "lidar_sample_list.txt") + \
                    " -intensity -step 1 -average -gray -ocut 4 -odir " + odir + " -otif -cores 4")


def main():
    
    # set up directories using dialog
    Tk().withdraw()                                                     # close empty tkinter window that opens by default
    idir_ortho = askdirectory(title='Select input ortho directory')     # prompt for directory with target orthophotos
    idir_lidar = askdirectory(title='Select input lidar directory')     # prompt for directory with lidar data
    odir = askdirectory(title='Select output directory')                # prompt for target output directory

    # run functions
    ortho_list = get_sample_images(idir_ortho, .05)                     # get random sample of dataset
    write_ortho_list(ortho_list, odir)                                  # make a list of files in sample for records
    copy_ortho_samples(ortho_list, odir)                                # copy samples to new location for convenience
    compress_samples(odir)                                              # compress, tile, and create overviews
    # os.remove(os.path.join(odir, 'ortho_samples'))                    # remove staging area directory for uncompressed ortho samples
    lidar_list = get_sample_lidar(ortho_list, idir_lidar)               # find any overlapping lidar data
    write_lidar_list(lidar_list, odir)                                  # write list of overlapping lidar data to text file
    make_intensity_grid(lidar_list, odir)                               # make intensity raster from overlapping lidar data


if __name__ == "__main__":
    main()