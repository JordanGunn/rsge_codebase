from rasterio.merge import merge
import rasterio as rio
from pathlib import Path
from tkinter import filedialog, simpledialog, Tk
from osgeo import gdal, ogr, osr
import numpy as np
from tqdm import tqdm
import os

# Create mosaic from multiple DEM files

root = Tk()
root.withdraw()

path = Path(filedialog.askdirectory(title="Select Directory Containing DEM or DSM .tif files"))
Path('output').mkdir(parents=True, exist_ok=True)
output_folder = (filedialog.askdirectory(title="Select Output Directory"))
output_path = output_folder+r"/Mosaic_Output.tif"

res = simpledialog.askfloat("Input", "Enter the desired output pixel resolution in meters between 1 and 5.\nA smaller resolution will result in a more accuracte extent, but will take longer.\nA larger resolution will result in a less accurate extent, but will take far less time\n", parent=root)

tif_files= []
raster_to_mosiac = []

for filename in os.listdir(path):
    if filename.endswith(".tif"):
        tif_files.append(os.path.join(path, filename))

for p in tqdm(tif_files):
    raster = rio.open(p)
    raster_to_mosiac.append(raster)

mosaic, output = merge(raster_to_mosiac, res=res)

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

ds = rio.open((os.path.join(output_folder,r"Mosaic_Output.tif")))

data = ds.read()

lista = data.copy()

lista[np.where((lista <=10000) & (lista >=-100))] = 1
lista[np.where((lista <-100) & (lista >=-9999))] = 0

with rio.open((os.path.join(output_folder,r"Mosaic_Reclass.tif")), 'w', driver = ds.driver, height = ds.height, width=ds.width, count=ds.count, crs=ds.crs, transform=ds.transform, dtype=data.dtype) as dst:
    dst.write(lista)

# Create geopackage boundary of mosaic

mosaic = (os.path.join(output_folder,r"Mosaic_Reclass.tif"))

mosaic1 = gdal.Open (mosaic)

band = mosaic1.GetRasterBand(1)

proj = mosaic1.GetProjection()

shp_proj = osr.SpatialReference()

shp_proj.ImportFromWkt(proj)

output_file = (os.path.join(output_folder,r"Valid_Raster_Area.gpkg"))

call_drive = ogr.GetDriverByName('GPKG')

create_gpkg = call_drive.CreateDataSource(output_file)

shp_layer = create_gpkg.CreateLayer('Extents', srs=shp_proj, geom_type=ogr.wkbPolygon)

new_field = ogr.FieldDefn(str('ID'), ogr.OFTInteger)

shp_layer.CreateField(new_field)

gdal.Polygonize(band, band, shp_layer, 0, [], callback=None)

create_gpkg.Destroy()

raster = None