#!/usr/bin/bash

# load config
chmod a+x "./db-config" && source "./db-config";
chmod a+x "./db-env" && source "./db-env";

# DB Table References
NAMESPACE="public"
TABLE_BCGS20K="${NAMESPACE}.BCGS20k"
TABLE_BCGS2500K="${NAMESPACE}.BCGS2500k"

# Create the database and tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USER_NAME}" -f "${SCRIPT_SCHEMA}"
echo "  Database creation and table generation complete."

# Populate the static reference tables
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USER_NAME}" -f "${SCRIPT_REFTABLE}"
echo "  Initial reference tables generated."

# Read and insert BCGS 2500K and 20K tile geometry into reference tables
echo "Creating BCGS reference tables ..."
# -- BCGS20K Grid insertion
chmod -R a+rw "${BCGS_SHP_DIR_20K}"
shp2pgsql -c -m "${COLUMN_MAP_20K}" -W "latin1" "${BCGS_SHP_20K}" "${TABLE_BCGS20K}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USER_NAME}"
echo "  BCGS20K reference table done."
# -- BCGS2500K Grid insertion
chmod -R a+rw "${BCGS_SHP_DIR_2500K}"
shp2pgsql -c -m "${COLUMN_MAP_2500K}" -W "latin1" "${BCGS_SHP_2500K}" "${TABLE_BCGS2500K}" | psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USER_NAME}"
echo "  BCGS2500K reference table done."

# Run post insertion
psql -h "${HOST_NAME}" -d "${DB_NAME}" -U "${USER_NAME}" -f "${SCRIPT_INSERTION}"
echo "================ Complete! ================"
