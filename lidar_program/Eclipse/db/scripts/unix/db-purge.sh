#!/usr/bin/bash

# load configuration params
source "./db-config"

# Drop the eclipse database
echo "Dropping the eclipse database..."
psql -U "${USERNAME}" -c "DROP DATABASE IF EXISTS ${DB_NAME};" || exit 1

echo "Database ${DB_NAME} has been removed."
