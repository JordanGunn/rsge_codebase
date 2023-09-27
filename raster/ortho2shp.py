from rasterio.merge import merge
import rasterio as rio
from pathlib import Path
from tkinter import filedialog
from osgeo import gdal, ogr, osr
import numpy as np
from tqdm import tqdm
import os

# Create mosaic from multiple DEM files

path = Path(filedialog.askdirectory(title="Select Directory Containing Ortho"))
Path('output').mkdir(parents=True, exist_ok=True)
output_folder = (filedialog.askdirectory(title="Select Output Directory"))
output_path = output_folder+r"/mosaic_output.tif"

raster_files = list(path.iterdir())
raster_to_mosiac = []

for p in tqdm(raster_files):
    raster = rio.open(p)
    raster_to_mosiac.append(raster)

mosaic, output = merge(raster_to_mosiac,res=30)

output_meta = raster.meta.copy()
output_meta.update(
    {"driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": output,
    }
)

with rio.open(output_path, "w", **output_meta) as m:
    m.write(mosaic)


# Reclassify mosaic so all valid pixels have a value of 1

ds = rio.open((os.path.join(output_folder,r"mosaic_output.tif")))

data = ds.read()

lista = data.copy()

lista[np.where((lista >0) & (lista <255))] = 1
lista[np.where ((lista <=0) &(lista >=255))] = 0


with rio.open((os.path.join(output_folder,r"mosaic_reclass.tif")), 'w', driver = ds.driver, height = ds.height, width=ds.width, count=ds.count, crs=ds.crs, transform=ds.transform, dtype=data.dtype) as dst:
    dst.write(lista)


# Create .shp boundary of mosaic

mosaic = (os.path.join(output_folder,r"mosaic_reclass.tif"))

mosaic1 = gdal.Open (mosaic)

band = mosaic1.GetRasterBand(2)

proj = mosaic1.GetProjection()

shp_proj = osr.SpatialReference()

shp_proj.ImportFromWkt(proj)

output_file = (os.path.join(output_folder,r"Ortho_Polygon.shp"))

call_drive = ogr.GetDriverByName('ESRI Shapefile')

create_shp = call_drive.CreateDataSource(output_file)

shp_layer = create_shp.CreateLayer('layername', srs = shp_proj)

new_field = ogr.FieldDefn(str('ID'), ogr.OFTInteger)

shp_layer.CreateField(new_field)

gdal.Polygonize(band, band, shp_layer, 0, [], callback = None)

create_shp.Destroy()

raster = None