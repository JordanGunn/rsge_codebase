#!/usr/bin/bash

# load config
chmod a+x "./db-config" && source "./db-config";
chmod a+x "./db-env" && source "./db-env";

# DB Table References
TABLE_BCGS20KGrid="eclipse.BCGS20K"
TABLE_BCGS2500KGrid="eclipse.BCGS2500K"

# Create the eclipse database
createdb -h "${HOST_NAME}" -U "${USERNAME}" "${DB_NAME}"
echo "  Created eclipse database."

# Set the roles and privileges
psql -h "${HOST_NAME}" -U "${USERNAME}" -d "${DB_NAME}" -f "${SCRIPT_ROLES}"
echo "  Roles and privileges set."

# Create the database and tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}" -f "${SCRIPT_SCHEMA}"
echo "  Database creation and table generation complete."

# Populate the static reference tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}" -f "${SCRIPT_REF_TABLE}"
echo "  Initial reference tables generated."

# Read and insert BCGS 2500K and 20K tile geometry into reference tables
echo "Creating BCGS reference tables ..."
shp2pgsql -s "${EPSG_ALBERS_CSRS}" -c -m "${COLUMN_MAP_20K}" -W "latin1" "${BCGS_SHP_20K}" "${TABLE_BCGS20KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"
echo "  BCGS20K reference table done."
shp2pgsql -s "${EPSG_ALBERS_CSRS}" -c -m "${COLUMN_MAP_2500K}" -W "latin1" "${BCGS_SHP_2500K}" "${TABLE_BCGS2500KGrid}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}"
echo "  BCGS2500K reference table done."

# Run post insertion
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USERNAME}" -f "${SCRIPT_POST_INERTION}"
echo "================ Complete! ================"



# ==============================================================================

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