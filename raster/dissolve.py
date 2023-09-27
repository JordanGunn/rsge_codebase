import geopandas as gpd

shp = R'C:\Users\breedwar\Downloads\valid_image_area_2022-01-20.shp'

img = gpd.read_file(shp)
img = img[['geometry']]

diss = img.dissolve()
print(diss)