#!/usr/bin/bash

# Environment Variables
ROOT_2500K="../data/BCGS_2500K"
INPUT_SHP="${ROOT_2500K}/BCGS_2500_GRID/BCGS2500GR_polygon.shp"  # Path to the input shapefile that contains all the tiles
TILE_FLIST="${ROOT_2500K}/tile_names_2500k"  # Temporary file for holding tile names
SHP_OUT_DIR="${ROOT_2500K}/tiles"  # Relative output path
TILE_NAME_COL="MAP_TILE"  # Map tile attribute table column name

# Extract unique tile names (MAP_TILE) from the shapefile and store them in the temp file
ogrinfo -al -geom=NO -q "${INPUT_SHP}" | grep "${TILE_NAME_COL}" | awk '{print $NF}' > "${TILE_FLIST}"

# Loop over each unique tile name
while read -r tile_name; do
  # Create a directory for the tile if it doesn't exist
  mkdir -p "${SHP_OUT_DIR}/$tile_name"

  # Use ogr2ogr to extract the tile and save it in its own shapefile inside the corresponding folder
  ogr2ogr -where "${TILE_NAME_COL}='$tile_name'" "${SHP_OUT_DIR}/$tile_name/$tile_name.shp" ${INPUT_SHP}

done < "${TILE_FLIST}"

# Remove the temporary file
# rm $TILE_FLIST