#!/usr/bin/bash

# load configuration params
source "./db-config.sh"

# Variable pre-declarations
export FLIST_20K;
export FLIST_2500K;

# Environment Variables
EPSG_ALBERS_CSRS=3153
DATA_DIR="../../../data"
SCRIPT_SCHEMA="./db_schema.sql"
SCRIPT_REF_TABLE="./db_ref.sql"
BCGS_ROOT_20K="${DATA_DIR}/BCGS_20K"
BCGS_ROOT_2500K="${DATA_DIR}/BCGS_2500K"
#BCGS_TILES_20K="${BCGS_ROOT_20K}/tiles"
#BCGS_TILES_2500K="${BCGS_ROOT_2500K}/tiles"
BCGS_SHP_20K="${BCGS_ROOT_20K}/BCGS_20K_GRID/20K_GRID_polygon.shp"
BCGS_SHP_2500K="${BCGS_ROOT_2500K}/BCGS_2500_GRID/BCGS2500GR_polygon.shp"

# DB Table References
TABLE_BCGS20KGrid="eclipse.BCGS20kGrid"
TABLE_BCGS2500KGrid="eclipse.BCGS2500kGrid"

# Create the database and tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}" -f "${SCRIPT_SCHEMA}"

# Populate the static reference tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}" -f "${SCRIPT_REF_TABLE}"

# Read and insert BCGS 2500K and 20K tile geometry into reference tables
shp2pgsql -s "${EPSG_ALBERS_CSRS}" -c -m "./col-map" -W "latin1" "${BCGS_SHP_20K}" "${TABLE_BCGS20KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"
shp2pgsql -s "${EPSG_ALBERS_CSRS}" -c -m "./col-map" -W "latin1" "${BCGS_SHP_2500K}" "${TABLE_BCGS2500KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"

## Get list of 2500K and 20K shapefiles
#FLIST_20K=$(find "${BCGS_TILES_20K}" -type f -name "*.shp")
#FLIST_2500K=$(find "${BCGS_TILES_2500K}" -type f -name "*.shp")
#
## Loop through each 20K shapefile and insert its geometry into the reference table
#for shapefile in $FLIST_20K; do
#  shp2pgsql -s "${EPSG_WGS84}" "${shapefile}" "${TABLE_BCGS20KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"
#done
#
## Loop through each 2500K shapefile and insert its geometry into the reference table
#for shapefile in $FLIST_2500K; do
#  shp2pgsql -s "${EPSG_WGS84}" "${shapefile}" "${TABLE_BCGS2500KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"
#done