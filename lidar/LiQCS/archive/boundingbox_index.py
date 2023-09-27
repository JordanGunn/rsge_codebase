from parseHeader import parseHeader
from math import floor,ceil
import geopandas as gpd

import geopandas as gpd

import shapely
import glob
import sys
import os

import datetime
import time

from tkinter import filedialog
from tkinter import Tk


def create_bounding_box(file):
    """Create a bounding box from lidar data and return WKT polygon"""
    # parse las/laz header body
    hdr = parseHeader(file, verbose=False)

    # gt min/max from las/laz header
    xmin, xmax, ymin, ymax = [hdr['xmin'], hdr['xmax'], hdr['ymin'], hdr['ymax']]

    # Create polygon from bounding box of las file
    bbox_poly = shapely.geometry.Polygon(
        [
            (xmin, ymax),
            (xmax, ymax),
            (xmax, ymin),
            (xmin, ymin),
            (xmin, ymax),
        ]
    )

    return bbox_poly


def create_tile_index(geom_list, file_list, epsg_code=None):
    """Append a list of geometry in WKT format to a GeoDataFrame"""
    gdf = gpd.GeoDataFrame(columns=["map_tile", "file", "geometry"])
    # assign spatial reference system metadata
    if epsg_code is not None:
        gdf.crs = {"init": f"epsg:{epsg_code}"}

    for geom, file in zip(geom_list, file_list):

        filename = os.path.basename(file)
        tile = filename[3:16]

        # append to dataframe
        gdf = gdf.append(
            {"map_tile": tile, "file": file, "geometry": geom},
            ignore_index=True
        )

    return gdf


def main():
    
    Tk().withdraw()

    # Specify input and output directory
    indir = filedialog.askdirectory(title='Select input directory')
    output = filedialog.askdirectory(title='Select directory for output')

    print("Specified a test that requires defining a CRS\n"
            "\nEPSG 2955: NAD83(CSRS) / UTM zone 11"
            "\nEPSG 3157: NAD83(CSRS) / UTM zone 10"
            "\nEPSG 3156: NAD83(CSRS) / UTM zone 9"
            "\nEPSG 3155: NAD83(CSRS) / UTM zone 8"
            "\nEPSG 3154: NAD83(CSRS) / UTM zone 7"
            "\nEPSG 3005: NAD83 / BC Albers\n"
            )
    epsg = int(input("Please enter EPSG code:\t"))

    # change directory to output location
    os.chdir(output)

    # gather list of all las or laz files in directories and sub-directories
    las_list = glob.glob(os.path.join(indir, '**/*.las'), recursive=True)
    laz_list = glob.glob(os.path.join(indir, '**/*.laz'), recursive=True)
    las_list.extend(laz_list)

    # create list of geometry
    tiles = [create_bounding_box(f) for f in las_list]

    # create tile index
    gdf = create_tile_index(tiles, las_list, epsg_code=epsg)

    # write gdf to geopackage
    gdf.to_file(f'{output}\\bbox_tiles_delivered_{datetime.date.today()}.gpkg', driver='GPKG')

if __name__ == '__main__':
    main()
