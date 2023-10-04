@echo off
setlocal enabledelayedexpansion

REM Params (Change as needed)
set DB=eclipse
set EPSG_ALBERS_CSRS=3005
set DIR_SCRIPT_DATA=..\data
set DIR_VECTOR_DATA=%USERPROFILE%\work\geobc\vector_data  REM --> CHANGE TO DATA LOCATION

REM Relative paths to SQL scripts
set PATH_SQL_SCRIPTS=..\..
set SCRIPT_ROLES=%PATH_SQL_SCRIPTS%\%DB%_roles.sql
set SCRIPT_SCHEMA=%PATH_SQL_SCRIPTS%\%DB%_schema.sql
set SCRIPT_REFTABLE=%PATH_SQL_SCRIPTS%\%DB%_reftables.sql
set SCRIPT_INSERTION=%PATH_SQL_SCRIPTS%\%DB%_insertion.sql

REM Relative paths to files containing data
set COLUMN_MAP_20K=%DIR_SCRIPT_DATA%\col-map-20K
set COLUMN_MAP_2500K=%DIR_SCRIPT_DATA%\col-map-2500K

REM Paths to data (Change as needed)
set BCGS_ROOT_20K=%DIR_VECTOR_DATA%\BCGS_20K
set BCGS_ROOT_2500K=%DIR_VECTOR_DATA%\BCGS_2500K
set BCGS_SHP_DIR_20K=%BCGS_ROOT_20K%\BCGS_20K_GRID
set BCGS_SHP_DIR_2500K=%BCGS_ROOT_2500K%\BCGS_2500_GRID
set BCGS_SHP_20K=%BCGS_SHP_DIR_20K%\20K_GRID_polygon.shp
set BCGS_SHP_2500K=%BCGS_SHP_DIR_2500K%\BCGS2500GR_polygon.shp
