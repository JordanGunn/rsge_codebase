#!/usr/bin/bash

# Load your config and environment variables
chmod a+x "./db-config" && source "./db-config";
chmod a+x "./db-env" && source "./db-env";

SCRIPT_PURGE="${PATH_SQL_SCRIPTS}/eclipse_purge.sql"

# Run the SQL script
psql -h "${HOST_NAME}" -U "${USER_NAME}" -d "${DB_NAME}" -a -f "${SCRIPT_PURGE}"
