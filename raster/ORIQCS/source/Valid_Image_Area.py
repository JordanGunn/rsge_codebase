import logging
# from tkinter import Tk
import os
from collections import defaultdict
from datetime import datetime

# import rasterio.control
import fiona
import geopandas as gpd
import numpy as np
import rasterio as rio
import rasterio.features
from fiona.crs import to_string
from shapely import speedups
from shapely.geometry import Polygon, mapping, shape
from shapely.geometry.multipolygon import MultiPolygon

'''
This code will output a shapefile that delineates the actual image area
of an ortho image. It assumes the nodata area of the ortho image is black (0,0,0).
It currently works with only geotiff images, but formats could be expanded.

Written By: Brett Edwards
'''


def create_mask_coordinates(image, nodata):
    with rio.open(image) as src:
        # Get source CRS
        crs = src.read_crs()

        # Get all 3 bands as arrays
        band1 = src.read(1)
        band2 = src.read(2)
        band3 = src.read(3)

        # Conditions need to be done in 2 steps.
        # Find where each band is 0 for all 3 pixels
        c1 = np.logical_and(band1 == nodata, band2 == nodata)
        c2 = np.logical_and(c1, band3 == nodata)

        # Assign 255 to all image area, 0 to no data area.
        # GDAL requires these values
        mask = (~c2 * 255).astype('uint8')

        # Create geojson polygons for all 255 mask values
        shapes = rio.features.shapes(mask, transform=src.transform)

        return shapes, crs


def get_shapefile_schema():
    # set schema for the output shapefile
    shp_schema = {
        'geometry': 'MultiPolygon',
        'properties': {'id': 'str'}
    }

    return shp_schema


def create_multipolygons(image, nodata, threshold=1):
    shapes, crs = create_mask_coordinates(image, nodata)

    # Add polygon to list, if the value is > 0.
    # All image areas will have a masked value of 255,
    # non image areas have a value of 0.
    polygons = [
        shape(geom) for geom,
        value in shapes if value > threshold
    ]

    # Create multipolygons using shapely
    multipolygons = MultiPolygon(polygons)

    return mapping(multipolygons), crs


def get_database_schema(database_path: str, layer_name: str) -> dict:
    """
    Gets the schema from a specific layer in a geopackage database

    Args:
        database_path: path to geopackage file
        layer_name: name of the layer in the geopackage to get the schema from

    Returns:
        Dict - representing the schema of the specified layer
    """

    with fiona.open(database_path, layer=layer_name) as db:
        layer_schema = db.schema

    return layer_schema


def read_shapefile_to_gpd(shapefile_path: str) -> gpd.GeoDataFrame:
    """
    Reads shapefile into a geopandas dataframe

    Args:
        shapefile_path: path to shapefile

    Returns:
        Geopandas dataframe  
    """
    gdf = gpd.read_file(shapefile_path)

    return gdf


def add_fields_from_schema(geodataframe: gpd.GeoDataFrame, schema: dict) -> gpd.GeoDataFrame:
    """
    Add fields to a geodataframe from a dictionary of schema read using fiona

    Args:
        geodataframe: Geopandas dataframe
        schema: fiona schema dictionary

    Returns:
        Geopandas dataframe  
    """
    fields = schema['properties'].keys()

    for field in fields:
        geodataframe[field] = None

    return geodataframe


def remove_fields_not_in_schema(geodataframe: gpd.GeoDataFrame, schema: dict) -> gpd.GeoDataFrame:
    """
    Remove fields from a geodataframe if they are not in the desired schema

    Args:
        geodataframe: Geopandas dataframe
        schema: fiona schema dictionary

    Returns:
        Geopandas dataframe  
    """
    schema_fields = schema['properties'].keys()

    for field in geodataframe.columns:
        if field not in schema_fields and field != 'geometry':
            geodataframe.drop(field, inplace=True, axis=1)

    return geodataframe


def fill_year_field(
        geodataframe: gpd.GeoDataFrame, year_field='year_of_acquisition') -> gpd.GeoDataFrame:
    """
    Fill the year field with the year from the 'id' field, which created from the source file name

    Args:
        geodataframe: Geopandas dataframe
        year_field: name of year field to be filled

    Returns:
        Geopandas dataframe
    """
    geodataframe[year_field] = geodataframe['id'].str.extract(
        '_(20[\d]{2})')  # if this doesn't find the year, it will fill the cell with NaN
    geodataframe[year_field] = geodataframe[year_field].fillna(0).astype(
        int)  # NaN can cause problems on writing with data types, we want this to be an int

    return geodataframe


def update_schema_attributes(geodataframe: gpd.GeoDataFrame, schema: dict) -> gpd.GeoDataFrame:
    """
    Add, remove, and update fields of a geodataframe to match a specific schema

    Args:
        geodataframe (gpd.GeoDataFrame): Geopandas dataframe
        schema (dict): fiona schema dictionary

    Returns:
        gpd.GeoDataFrame: Geopandas dataframe
    """

    geodataframe = add_fields_from_schema(geodataframe, schema=schema)
    geodataframe = fill_year_field(geodataframe)
    geodataframe = remove_fields_not_in_schema(geodataframe, schema=schema)

    return geodataframe


def dissolve_polygons_by(
        layer_to_dissolve: str, dissolve_field='year_of_acquisition', database_path: str = None,
        layer_name: str = None) -> gpd.GeoDataFrame:
    """
    Dissolves a geodataframe by year, while updating schemas to match a geopackage database layer

    Args:
        layer_to_dissolve (str): Path to spatial file to dissolve
        dissolve_field (str, optional): Field to dissolve on. Defaults to 'year_of_acquisition'.
        database_path (str, optional): Path to geopackage file. Defaults to None.
        layer_name (str, optional): Name of the layer in the geopackage to get the schema from. 
        Defaults to None.

    Returns:
        gpd.GeoDataFrame: Dissolved geopandas dataframe
    """
    valid_image_gdf = read_shapefile_to_gpd(layer_to_dissolve)

    if database_path and layer_name:
        schema = get_database_schema(database_path, layer_name)
        update_schema_attributes(valid_image_gdf, schema=schema)
    dissolved_gdf = valid_image_gdf.dissolve(by=dissolve_field)

    return dissolved_gdf


def export_dissolved_geodataframe(
        gdf: gpd.GeoDataFrame, outfile: str, layer_name: str, projection='EPSG:3005'):
    """
    Export a geodataframe to a geopackage

    Args:
        gdf (gpd.GeoDataFrame): Geopandas dataframe
        outfile (str): Path to geopackage
        layer_name (str): Layer name within geopackage
        projection (str, optional): EPSG code for geopackage layer. Defaults to 'EPSG:3005'.
    """
    gdf_albers = gdf.to_crs(
        projection)  # Before export, transform to whatever projection we want

    # let's say every gdf that gets exported gets it's area calculated in sqkm, why not
    gdf_albers['area_sqkm'] = round(gdf_albers['geometry'].area / 10**6, 2)

    try:
        gdf_albers.to_file(outfile, layer=layer_name)
    except Exception as e:
        logging.error(str(e))


def get_hole_geometries(geopackage_path: str, layer_name: str) -> defaultdict:
    """
    Gets the geometries of the interior polygons, or holes, within the provided 

    Args:
        geopackage_path (str): Full path to geopackage
        layer_name (str): Layer name within the geopackage

    Returns:
        Hole geometries (collections.defaultdict): A defaultdict containing geometries of holes 
                                                   in the layer
    """
    tile_holes = defaultdict(list)

    with fiona.open(geopackage_path, layer=layer_name) as tile_polys:
        for tile in tile_polys:
            polygons = MultiPolygon(shape(tile['geometry']))
            for geom in polygons.geoms:
                if len(geom.interiors):
                    for interior in geom.interiors:
                        hole_coords = interior.coords[:]
                        tile_name = tile['properties']['id']
                        tile_holes[tile_name].append(hole_coords)

    return tile_holes


def write_geometries(geopackage_path: str, layer_name: str, geometries: defaultdict, crs: str):
    """
    Write geometries to a specific schema and geometry type to a geopackage.

    TODO This should be altered to be more flexible, writing geometries of different types
    and schemas

    Args:
        geopackage_path (str): path to geopackage 
        layer_name (str): layer name within the geopackage
        geometries (defaultdict): dict with tile id's as keys and geometries as values
        crs (str): EPSG code to write the geometries in. This is a definition, not a transformation.
    """
    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'str'}
    }

    mode = 'w'
    if gpkg_layer_exists(geopackage_path, layer_name):
        mode = 'a'

    with fiona.open(geopackage_path, layer=layer_name, mode=mode, driver='GPKG', schema=schema, crs=crs) as holes:
        for tile, coords in geometries.items():
            for coord in coords:
                # geom = MultiPolygon([(shape(Polygon(coord)) for coord in coords)])
                geom = Polygon(coord)
                holes.write({
                    'geometry': mapping(geom),
                    'properties': {'id': tile}
                })


def gpkg_layer_exists(geopackage_path: str, layer_name: str) -> bool:
    """
    Check to see if layer exists within a geopackage

    Args:
        geopackage_path (str): Path to geopackage
        layer_name (str): Layer name within geopackage

    Returns:
        bool: True or False
    """
    if layer_name in fiona.listlayers(geopackage_path):
        return True
    return False


def main(nodata):
    import glob
    from tkinter import filedialog

    today = datetime.today().strftime('%Y-%m-%d')
    # Tk().withdraw()  # close default empty tkinter window

    # prompt for input and output directory
    # idir = filedialog.askdirectory(title="Select input orthoimage directory")
    # odir = filedialog.askdirectory(title="Select output location")

    idir = R'C:\projects\dissolve_ortho\no_holes_sample'
    odir = R'C:\projects\dissolve_ortho\no_holes_sample\out'

    odir += '\Valid_Image_Area'
    if not os.path.exists(odir):
        os.makedirs(odir)

    # specify the output file name. Delete the file if it already exists.
    outfile = f'{odir}\\valid_image_area_{today}.gpkg'
    if os.path.exists(outfile):
        os.remove(outfile)

    log_file = os.path.join(odir, 'valid_image_errors.log')

    # set up basic logging configuration
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    # create file list of orthos, could add more formats? MrSid currently not working in Python
    extensions = ("*.tif", "*.tiff")
    flist = []
    for extension in extensions:
        flist.extend(glob.glob(idir + "/" + extension))

    # set a place to store the CRS
    project_crs = None

    # get shapefile schema for output
    shp_schema = get_shapefile_schema()

    # loop through images and write each shape to the output shapefile
    speedups.disable()
    for image in flist:
        basename = image.split('\\')[-1]

        # set up a try/except for the logger
        try:
            multipolygons, crs = create_multipolygons(image, nodata)
        except Exception as e:
            logging.error(image + '; ' + str(e))

        if project_crs == None:  # if the project CRS is not set, take it from the first image with a valid CRS
            project_crs = to_string(crs)

        # need 'w' mode to create the shapefile, and 'a' (append) mode to append shapes
        mode = 'w'
        if os.path.exists(outfile):
            mode = 'a'

        with fiona.open(outfile, mode=mode, driver='GPKG', layer='valid_image_tiles', schema=shp_schema, crs=project_crs) as shp:

            shp.write({                             # write to shapefile
                'geometry': multipolygons,
                'properties': {'id': basename}
            })

    dissolved_gdf = dissolve_polygons_by(
        layer_to_dissolve=outfile,
        dissolve_field='year_of_acquisition',
        database_path=R'\\sfp.idir.bcgov\s164\S63063\ILMB_CRIM_BMGS\PBA\Top_Common\__PROJECTS__\Database\GeoBC_LiDAR_Imagery_Coverage.gpkg',
        layer_name='Imagery_Coverage')

    export_dissolved_geodataframe(dissolved_gdf, outfile, 'image_coverage')

    holes = get_hole_geometries(outfile, layer_name='valid_image_tiles')

    write_geometries(outfile, 'image_holes', holes, project_crs)

    if os.stat(log_file).st_size > 0:
        print('\n*******Errors occurred, check log file')


def run_from_gui(flist, odir, nodata):
    today = datetime.today().strftime('%Y-%m-%d')

    odir += '\Valid_Image_Area'
    if not os.path.exists(odir):
        os.makedirs(odir)

    # Specify the output file name. Delete the file if it already exists.
    outfile = f'{odir}\\valid_image_area_{today}.gpkg'
    if os.path.exists(outfile):
        os.remove(outfile)

    log_file = os.path.join(
        odir,
        'valid_image_errors.log'
    )

    # Set up basic logging configuration
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    '''
    # create file list of orthos, could add more formats? MrSid currently not working in Python
    extensions= ("*.tif", "*.tiff")
    flist = []
    for extension in extensions:
        flist.extend(glob.glob(idir+"/"+extension))
    '''

    # Set a place to store the CRS
    project_crs = None

    # Get shapefile schema for output
    shp_schema = get_shapefile_schema()

    # Loop through images and write each shape to the output shapefile
    speedups.disable()
    for image in flist:
        basename = image.split('\\')[-1]

        # Set up a try/except for the logger
        try:
            multipolygons, crs = create_multipolygons(image, nodata)
        except Exception as e:
            logging.error(f"{image}; {str(e)}")

        # If the project CRS is not set, take it
        # from the first image with a valid CRS
        if not project_crs:
            project_crs = to_string(crs)

        # Need 'w' mode to create the shapefile, and 'a' (append) mode to append shapes
        mode = 'w'
        if os.path.exists(outfile):
            mode = 'a'

        with fiona.open(
            outfile,
            mode=mode,
            driver='GPKG',
            layer='valid_image_tiles',
            schema=shp_schema,
            crs=project_crs
        ) as shp:

            # Write to shapefile
            shp.write(
                {
                    'geometry': multipolygons,
                    'properties': {'id': basename}
                }
            )

    # TODO The section above should be refactored
    ########################################################################################
    # The section below creates an ortho coverage layer and a layer representing the holes

    dissolved_gdf = dissolve_polygons_by(
        layer_to_dissolve=outfile,
        dissolve_field='year_of_acquisition',
        database_path=R'\\sfp.idir.bcgov\s164\S63063\ILMB_CRIM_BMGS\PBA\Top_Common\__PROJECTS__\Database\GeoBC_LiDAR_Imagery_Coverage.gpkg',
        layer_name='Imagery_Coverage')

    export_dissolved_geodataframe(
        dissolved_gdf, outfile, 'valid_image_coverage')

    holes = get_hole_geometries(outfile, layer_name='valid_image_tiles')

    write_geometries(outfile, 'image_holes', holes, project_crs)

    if os.stat(log_file).st_size > 0:
        print('\n*******Errors occurred, check log file')


if __name__ == '__main__':
    main(nodata=0)
