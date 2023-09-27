# Created by Spencer Floyd

from osgeo import gdal
import numpy as np
from tkinter import filedialog
from matplotlib import pyplot as plt


# Open density raster and shapefile (no water areas)
raster = filedialog.askopenfilename(initialdir="/", title="Select Density Grid", filetypes=(("tif files","*.tif"),("all files", "*.*")))
vector = filedialog.askopenfilename(initialdir="/", title="Select Vector File", filetypes=(("shp files","*.shp"),("all files", "*.*")))

# Open denisty raster with GDAL
ds = gdal.Open (raster)

# Clip density raster to AOI
clip = gdal.Warp("clip.tif", ds, cutlineDSName = vector, cropToCutline =True)

# Get raster band from clipped density grid
band = clip.GetRasterBand(1)

#Ignore no data values
ndv = ds.GetRasterBand(1).GetNoDataValue()

# Create array from density grid band
array = band.ReadAsArray()

# Convert ndv to nan
array [array==ndv] = np.nan

# Ignore nan values
array = array[np.logical_not(np.isnan(array))]

# Reclassify array so all values under 8 are set to the value "1" and the rest is set to "0"
mask =np.where(array < 8, 1, 0)

# Count the number of values equal to "1" in array
count = np.count_nonzero(mask == 1)

# Create list from array
list = array.tolist()

# Calculate total number of values in array and percentage
total = len(list)
percentage = count/total

# Calculate real percentage
percent = percentage*100

# Define mean line and text for histogram
def add_mean_line(array):
    mu = np.mean(array)

    ax=plt.gca()


    ax. text(0.7,0.9, f'Mean = {mu:.2f}',
        transform=ax.transAxes,
        fontweight='bold', fontsize=12)

# Define percent text for histogram
def add_percentage(array):
    pr = percent

    ax=plt.gca()

    ax. text(0.5,0.8, f'{pr:.2f}% under 8 points/m2',
        transform=ax.transAxes,
        fontweight='bold', fontsize=12)

# Plot histogram
plt.hist(array,bins = 500, color="red")
add_mean_line(array)
add_percentage(array)
min_ylim, max_ylim = plt.ylim()
plt.title("lidar Density", fontsize=15)
plt.ylabel("Frequency")
plt.xlabel("Points Per Square Meter")
plt.xlim(0,60)
plt.show()