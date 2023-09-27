from gdalnumeric import BandWriteArray, BandReadAsArray, CopyDatasetInfo
from scipy.stats import norm
from laspy.file import File
from math import floor,ceil

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import geopandas as gpd
import pandas as pd
import numpy as np

import subprocess
import argparse
import sys
import os

import gdal
import osr
import shapely

import struct
import glob
import csv
import re

import datetime
import time

from tkinter import filedialog
from tkinter import Tk
import glob
import laspy
import numpy

def lasinfo_density(lasinfo, last_return=False):
    """Extract density from lasinfo txt file"""
    # open lasinfo file
    open_info = open(lasinfo, "r")
    # find index value of point density information
    for line in open_info:
        if 'point density' in line:
            # get density values and convert to float
            try:
                if last_return:
                    dens = float(line.split(' ')[-4])
                else:
                    dens = float(line.split(' ')[4])
                return dens
            except:
                print(f'Error getting density value from {lasinfo}')
                pass
    
    open_info.close()


def density_histogram(dataset, path, custom_title=None):
    """create histogram for density values"""
    # best fit of data
    (mu, sigma) = norm.fit(dataset)

    # the histogram of the data
    n, bins, patches = plt.hist(dataset, 15, density=1, facecolor='blue', alpha=0.75)

    # add a 'best fit' line
    # Changed mlab.normpdf() to scipy.stats.norm.pdf(), mlab version is deprecated
    y = norm.pdf(bins, mu, sigma)
    l = plt.plot(bins, y, 'y--', linewidth=2)

    #plot
    plt.xlabel('Density (points/sq. m)')
    plt.ylabel('Frequency')
    if custom_title is not None:
            plt.title = (f'{custom_title}:  mu={mu}  sigma={sigma}')
    else:
        plt.title(r'$\mathrm{Histogram\ of\ Density:}\ \mu=%.3f,\ \sigma=%.3f$' %(mu, sigma))

    plt.grid(True)

    plt.savefig(f'{path}.png')
    plt.close()
    

def make_density_histograms(lasinfo_glob, outdir):
    """Creating last return and ground point density histograms"""
    
    try:
        lr_dens_none = [lasinfo_density(f, last_return=True) for f in lasinfo_glob]
        lr_dens = [d for d in lr_dens_none if d]  # remove values equal to None   !!! Fixed bug causing ground dens histogram to not be created 2019-10-24 :: By Jordan !!!
        density_histogram(lr_dens,outdir+'\\last_return_density', custom_title="Last Return Density")
    except:
        print('Error creating last return density statistics')
        pass

    try:
        ground_dens_none = [lasinfo_density(f, last_return=False) for f in lasinfo_glob]  # may have values equal to None
        ground_dens = [d for d in ground_dens_none if d]  # remove values equal to None   !!! Fixed bug causing ground dens histogram to not be created 2019-10-24 :: By Jordan !!!
        density_histogram(ground_dens,outdir+'\\ground_density', custom_title="All returns density")
    except:
        print('Error creating ground density statistics, file may contain no ground points')
        pass

def main():

    Tk().withdraw()

    # Specify input and output directory
    indir = filedialog.askdirectory(title='Select input directory of lasinfo files')
    output = filedialog.askdirectory(title='Select directory for output')

    os.chdir(output)

    # gather list of all las or laz files in directories and sub-directories
    lasinfo_list = glob.glob(os.path.join(indir, '**/*.txt'), recursive=True)

    print(lasinfo_list)

    # make the histograms
    make_density_histograms(lasinfo_list, output)


if __name__ == '__main__':
    main()


