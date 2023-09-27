import rasterio as rio 
import rasterio.features
import fiona
from fiona.crs import to_string
from shapely.geometry import shape, mapping
from shapely.geometry.multipolygon import MultiPolygon
import numpy as np
from tkinter import Tk
from tkinter import filedialog
import os
import glob
from datetime import datetime
from tqdm import tqdm
import logging

'''
This code will output a shapefile that delineates the actual image area 
of an ortho image. It assumes the nodata area of the ortho image is black (0,0,0).
It currently works with only geotiff images, but formats could be expanded.

Written By: Brett Edwards
'''



def create_mask_coordinates(image, nodata=0):
        with rio.open(image) as src:
            crs = src.read_crs()    # get source CRS
            
            band1 = src.read(1)     # get all 3 bands as arrays
            band2 = src.read(2)
            band3 = src.read(3)

            # conditions need to be done in 2 steps. Find where each band = 0 for all 3 pixels
            c1 = np.logical_and(band1==nodata, band2==nodata)   
            c2 = np.logical_and(c1, band3==nodata)

            mask = (~c2*255).astype('uint8')    # assign 255 to all image area, 0 to no data area. GDAL requires these values
            
            shapes = rio.features.shapes(mask, transform=src.transform)     # create geojson polygons for all 255 mask values

            return shapes, crs

def get_shapefile_schema():
    # set schema for the output shapefile
    shp_schema = {
    'geometry': 'MultiPolygon',
    'properties': {'id': 'str'}
    }

    return shp_schema

def create_multipolygons(image, threshold=1):
    shapes, crs = create_mask_coordinates(image)

    polygons = [shape(geom) for geom, value in shapes if value>threshold]       # add polygon to list, if the value is > 0. All image areas will have a masked value of 255, non image areas have a value of 0.

    multipolygons = MultiPolygon(polygons)  # create multipolygons using shapely

    return mapping(multipolygons), crs


def main():
    today = datetime.today().strftime('%Y-%m-%d')
    Tk().withdraw()  # close default empty tkinter window

    # prompt for input and output directory
    idir = filedialog.askdirectory(title="Select input orthoimage directory")
    odir = filedialog.askdirectory(title="Select output location")
    # idir = R'C:\Projects\work\ortho'
    # odir = R'C:\Projects\work\ortho'

    outfile = f'{odir}\\valid_image_area_{today}.shp' # specify the output file name. Delete the file if it already exists.
    if os.path.exists(outfile):
        os.remove(outfile)

    log_file = os.path.join(odir,'valid_image_errors.log')

    # set up basic logging configuration
    logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


    # create file list of orthos, could add more formats? MrSid currently not working in Python
    flist = [f for f in glob.glob(f'{idir}\\**\*',recursive=True)
                   if f[-4:] in {'.tif'}]

    # set a place to store the CRS
    project_crs = None

    # get shapefile schema for output
    shp_schema = get_shapefile_schema()

    # loop through images and write each shape to the output shapefile
    for image in tqdm(flist):
        basename = image.split('\\')[-1]

        # set up a try/except for the logger    
        try:
            multipolygons, crs = create_multipolygons(image)
        except Exception as e:
            logging.error(image+'; '+e)
        

        if project_crs==None:  # if the project CRS is not set, take it from the first image with a valid CRS
            project_crs = to_string(crs)

        mode = 'w'              # need 'w' mode to create the shapefile, and 'a' (append) mode to append shapes
        if os.path.exists(outfile):
            mode = 'a'

        with fiona.open(outfile, mode=mode, driver='ESRI Shapefile', schema=shp_schema, crs=project_crs) as shp:
    
            shp.write({                             # write to shapefile
                'geometry': multipolygons,
                'properties': {'id': basename}
            })

    if os.stat(log_file).st_size > 0:
        print('\n*******Errors occurred, check log file\nPress enter to exit')
        input()


if __name__=='__main__':
    main()