# Created by Jordan Godau
# Updated by Natalie Jackson
"""
This script opens a directory of raster images and computes the bounding box
of the image. Then it writes it to a shapefile in the user specified directory.
It provides a method to check the area coverage of large imagery data-sets
without opening many large imagery files at a time. This script experiments
with modules such as geopandas and rasterio.
"""

import rasterio as rio
import geopandas as gpd
import os
import re
import glob
import pandas as pd
import datetime
from Image_Corruption import checkTif
from shapely.geometry import box
from shapely import speedups
from osgeo import osr
from fiona.crs import from_epsg
import concurrent.futures


def _map_tile_column_name():
    return 'map_tile'


def _input_file_column_name():
    return 'file'


def _geometry_column_name():
    return 'geometry'

def _contract_number_column_name():
    return 'contract_number'


def create_bounds(args):
    i, file, gdf = args
    try:
        #  open image and set image bound geometry
        image_bounds = rio.open(file).bounds
        base = os.path.basename(file)
        tile = base.split(".")[0]
        speedups.disable()

        new_record = {
            _map_tile_column_name(): tile,
            _input_file_column_name(): file,
            _geometry_column_name(): box(
                image_bounds[0],
                image_bounds[1],
                image_bounds[2],
                image_bounds[3]
            )
            
        }

        new_record_gdf = gpd.GeoDataFrame(new_record, index=[i])
        gdf = pd.concat((gdf, new_record_gdf), axis=0, ignore_index=True)

        return gdf

    except Exception:
        pass

def get_projections_and_type(image_file_list, outdir):
    orthoRegex = r'_x(c|ci|li|fc)(\d{3})mm_(utm07|utm08|utm09|utm10|utm11|bcalb)'
    fileByProduct={
        'DEM': {},
        'DSM': {},
        'Ortho': {},
        'Product_Not_found': {}
    }
    fileProductsNotFound = []

    for file in image_file_list:
        fileBasename = os.path.basename(file)
        fileProduct = ''
        if re.search('dsm', fileBasename):
            fileProduct = 'DSM'

        elif re.search('mm', fileBasename):
            orthoType = re.search(orthoRegex, fileBasename)
            if orthoType == None:
                fileProductsNotFound.append(file)
                continue
            orthoType = f'{orthoType.groups()[0]}_{orthoType.groups()[1]}mm'
            fileProduct = 'Ortho'

        elif re.search('_x(li|r|rgb)', fileBasename):
            fileProduct = 'DEM'
        else:
            fileProductsNotFound.append(file)
            continue

        if len(checkTif([file])) != 0:
            fileProductsNotFound.append(f'FILE IS CORRUPTED!!! --- {file}')
            continue

        epsg = rio.open(file).crs.to_epsg()
        if fileProduct == 'Ortho':
            if orthoType not in fileByProduct[fileProduct].keys():
                fileByProduct[fileProduct][orthoType] = {}
            if epsg not in fileByProduct[fileProduct][orthoType].keys():
                fileByProduct[fileProduct][orthoType][epsg] = []
            fileByProduct[fileProduct][orthoType][epsg].append(file)
        else:
            if epsg not in fileByProduct[fileProduct].keys():
                fileByProduct[fileProduct][epsg] = []
            fileByProduct[fileProduct][epsg].append(file)
    
    if len(fileProductsNotFound) > 0:
        with open(f'{outdir}\\products_not_found.txt', mode='w+') as errFile:
            errFile.write("The product type could not be found for the following file(s):\n")
            for file in fileProductsNotFound:
                print(file, file=errFile)

    return fileByProduct

def create_gpkg(fileByEpsg, outdir, cores, contract_number):
    """
    Create a polygon shapefile where each record (polygon)
    is a bounding box for each file in the input file list.

    Attributes of the polygons:
        - map_tile: The map tile, parsed from the input file filename.
        - file: The full path of the input image file.

    Args:
        image_file_list (list of str): list of image file paths to create coverage tile index for
        outdir (str): main ORIQCS output directory
        cores (int): number of cores to use for processing
    """
    target = "raster_bbox_tile_index.shp"
    
    for epsg in fileByEpsg:
        fileList = fileByEpsg[epsg]
        # Call the mandatory SpatialReference() method to setup CRS
        tgt_spatRef = osr.SpatialReference()

        # define the spatial reference system for the output shapefile
        tgt_spatRef.ImportFromEPSG(epsg)

        # split the basename from the extension to be used to generate the prj file
        lyrName = os.path.splitext(target)[0]

        # set working directory to output location
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir(outdir)

        # create empty geodataframe to append to
        gdf = gpd.GeoDataFrame(
            columns=[
                _map_tile_column_name(),
                _input_file_column_name(),
                _geometry_column_name(),
                _contract_number_column_name(),
            ]
        )

        with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
            results = [
                executor.submit(create_bounds, [i, file, gdf]) for i, file in enumerate(fileList)
            ]

        for f in concurrent.futures.as_completed(results):
            try:
                result = f.result()
                gdf = pd.concat((gdf, result), axis=0)
                gdf['contract_number'] = contract_number
            except Exception as e:
                with open(f'{outdir}\\PPE_Exemptions.txt', mode='w+') as out:
                    print(f'Exception: {e}', file=out)

        # change directory to output location
        os.chdir(outdir)

        out_name = f"bbox_{contract_number}_{datetime.date.today()}.gpkg"
        bbox_tiles_gpkg = os.path.join(outdir, out_name)
        gdf.crs = from_epsg(epsg)

        # write geodataframe to shapefile
        try:
            gdf.to_file(bbox_tiles_gpkg, layer=str(epsg), driver='GPKG')
        except ValueError as e:
            with open(f'{outdir}\\Error.txt', mode='w+') as err:
                print(f'Exception: {e}', file=err)

def run_from_gui(image_file_list, outdir, cores, contract_number):

    baseOutdir = outdir + '/Tile_Index/'
    if not os.path.exists(baseOutdir):
        os.makedirs(baseOutdir)
    fileByProduct = get_projections_and_type(image_file_list, baseOutdir)
    
    #print(f'{fileByEpsg=}')
    for product in fileByProduct:
        if len(fileByProduct[product]) == 0:
            continue
        elif product == 'Ortho':
            for orthoType in fileByProduct[product].keys():
                orthoOut = outdir + f'/Tile_Index/{product}_Bounding_Boxes/{orthoType}'
                create_gpkg(fileByProduct[product][orthoType], orthoOut, cores, contract_number)
        else:
            prodOutdir = outdir + f'/Tile_Index/{product}_Bounding_Boxes'
            create_gpkg(fileByProduct[product], prodOutdir, cores, contract_number) 
                
if __name__ == "__main__":

    # image_file_list (list of str): list of image file paths to create coverage tile index for
    inputPath = r'C:\Imagery_tests\tile_index_test'
    extensions = [".tiff", ".tif"]
    for extension in extensions:
        image_file_list = glob.glob(inputPath + "\**/*" + extension, recursive=True)

    # outdir (str): main ORIQCS output directory
    outdir = r'C:\Users\smay1\Desktop\output'
    # cores (int): number of cores to use for processing
    cores = 4
    # contract_number (str): contract identifier
    contract_number = '12313'

    run_from_gui(image_file_list, outdir, cores, contract_number)