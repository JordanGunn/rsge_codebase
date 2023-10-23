setlocal enabledelayedexpansion

:: Configuration parameters for ECLIPSE
set HOST_NAME=localhost
set HOST_IP=127.0.0.1
set DB_NAME=eclipse
set USER_NAME=postgres
set PASSWORD=postgres

::posgresdb environment variable (do not change).
set PGPASSWORD=%PASSWORD%

REM Params (Change as needed)
set DB=eclipse
set EPSG_ALBERS_CSRS=3005
set DIR_SCRIPT_DATA=../data
set DIR_VECTOR_DATA=C:/GeoBC/vectors

REM Relative paths to SQL scripts
set PATH_SQL_SCRIPTS=..\..
set SCRIPT_ROLES=%PATH_SQL_SCRIPTS%\%DB%_roles.sql
set SCRIPT_SCHEMA=%PATH_SQL_SCRIPTS%\%DB%_schema.sql
set SCRIPT_REFTABLE=%PATH_SQL_SCRIPTS%/%DB%_reftables.sql
set SCRIPT_INSERTION=%PATH_SQL_SCRIPTS%/%DB%_insertion.sql

REM Relative paths to files containing data
set COLUMN_MAP_20K=%DIR_SCRIPT_DATA%/col-map-20K
set COLUMN_MAP_2500K=%DIR_SCRIPT_DATA%/col-map-2500K

REM Paths to data (Change as needed)
set BCGS_ROOT_20K=%DIR_VECTOR_DATA%/BCGS_20K
set BCGS_ROOT_2500K=%DIR_VECTOR_DATA%/BCGS_2500K
set BCGS_SHP_DIR_20K=%BCGS_ROOT_20K%/BCGS_20K_GRID
set BCGS_SHP_DIR_2500K=%BCGS_ROOT_2500K%/BCGS_2500_GRID
set BCGS_SHP_20K=%BCGS_SHP_DIR_20K%/20K_GRID_polygon.shp
set BCGS_SHP_2500K=%BCGS_SHP_DIR_2500K%/BCGS2500GR_polygon.shp

echo %BCGS_ROOT_20K%
echo %BCGS_ROOT_2500K%
echo %BCGS_SHP_DIR_20K%
echo %BCGS_SHP_DIR_2500K%
echo %BCGS_SHP_20K%
echo %BCGS_SHP_2500K%

set /p stuff=?

REM DB Table References
set NAMESPACE=public
set TABLE_BCGS20K=%NAMESPACE%.BCGS20k
set TABLE_BCGS2500K=%NAMESPACE%.BCGS2500k

:: Check if the database exists
for /f %%i in ('psql -h %HOST_NAME% -U %USER_NAME% -tAc "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'"') do set DB_EXISTS=%%i

:: If the database doesn't exist, create it
if "%DB_EXISTS%" neq "1" (
    psql -h %HOST_NAME% -U %USER_NAME% -c "CREATE DATABASE %DB_NAME%"
)

REM Create the database and tables
psql -h "%HOST_NAME%" -d "%DB_NAME%" -U "%USER_NAME%" -f "%SCRIPT_SCHEMA%"
echo   Database creation and table generation complete.

REM Populate the static reference tables
psql -h "%HOST_NAME%" -d "%DB_NAME%" -U "%USER_NAME%" -f "%SCRIPT_REFTABLE%"
echo   Initial reference tables generated.

REM Read and insert BCGS 2500K and 20K tile geometry into reference tables
echo Creating BCGS reference tables ...

REM -- BCGS20K Grid insertion
attrib -r "%BCGS_SHP_DIR_20K%\*.*" /S
shp2pgsql -c -m "%COLUMN_MAP_20K%" -W "latin1" "%BCGS_SHP_20K%" "%TABLE_BCGS20K%" | psql -h "%HOST_NAME%" -d "%DB_NAME%" -U "%USER_NAME%"
echo   BCGS20K reference table done.

REM -- BCGS2500K Grid insertion
attrib -r "%BCGS_SHP_DIR_2500K%\*.*" /S
shp2pgsql -c -m "%COLUMN_MAP_2500K%" -W "latin1" "%BCGS_SHP_2500K%" "%TABLE_BCGS2500K%" | psql -h "%HOST_NAME%" -d "%DB_NAME%" -U "%USER_NAME%"
echo   BCGS2500K reference table done.

REM Run post insertion
psql -h "%HOST_NAME%" -d "%DB_NAME%" -U "%USER_NAME%" -f "%SCRIPT_INSERTION%"
echo ================== Complete! ==================

endlocal
