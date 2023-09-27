# Created by Jordan Godau
# Click on script and follow prompts, no editing of script required

"""
This script opens a directory of raster images and computes the bounding box
of the image. Then it writes it to a shapefile in the user specified directory.
It provides a method to check the area coverage of large imagery data-sets
without opening many large imagery files at a time. This script experiments
with modules such as geopandas and rasterio.
"""

import rasterio
import geopandas as gpd
import os
import glob
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from shapely.geometry import box
from osgeo import osr
from tqdm import tqdm

Tk().withdraw()

# prompt for input directory
indir = filedialog.askdirectory(title='Select input image directory')
outdir = filedialog.askdirectory(title='Select output location')

# Request EPSG code for the spatial reference system
print('\nEPSG 2955: NAD83(CSRS) / UTM zone 11')
print('EPSG 3157: NAD83(CSRS) / UTM zone 10')
print('EPSG 3156: NAD83(CSRS) / UTM zone 9')
print('EPSG 3155: NAD83(CSRS) / UTM zone 8')
print('EPSG 3154: NAD83(CSRS) / UTM zone 7')
print('EPSG 3005: NAD83 / BC Albers\n')
epsg_str = input('Please enter the integer EPSG code for the desired projection: ')
print('\n\nPlease wait, processing...\n')

# target = (base[:(len(base)-4)]) + '_BB' '.shp'
target = "Imagery_BoundingBox.shp"

# Call the mandatory SpatialReference() method to setup CRS
tgt_spatRef = osr.SpatialReference()

# define the spatial reference system for the output shapefile
tgt_spatRef.ImportFromEPSG(int(epsg_str))

# split the basename from the extension to be used to generate the prj file
lyrName = os.path.splitext(target)[0]

# set working directory to output location
os.chdir(outdir)

# Create new file in the working directory to store projection information
if not os.path.exists(lyrName + '.prj'):
    prj = open(lyrName + ".prj", "w")

    # write spatial reference information in WKT format to new file
    prj.write(tgt_spatRef.ExportToWkt())
    prj.close()

# define an empty list to append to later
flist = []

# create empty geodataframe to append to
df = gpd.GeoDataFrame(columns=['map_tile', 'file', 'geometry'])

# create a list of all las files in user specified input directory
list = glob.glob(os.path.join(indir, '**/*.tif'), recursive=True)

for file in tqdm(list):
    try:
        #  open image and set image bound geometry
        image_bounds = rasterio.open(file).bounds
        base = os.path.basename(file)
        tile = base.split(".")[0]
        df = df.append({'map_tile': tile, 'file': file, 'geometry': box(image_bounds[0], image_bounds[1],
                                                        image_bounds[2], image_bounds[3])}, ignore_index=True)
    except:
        pass

# change directory to output location
os.chdir(outdir)

# write geodataframe to shapefile
df.to_file(target)
