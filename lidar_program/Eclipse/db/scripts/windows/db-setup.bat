@echo off
setlocal

:: Load configuration params
call ".\db-config.bat"

:: Environment Variables
set EPSG_WGS84=4326
set DATA_DIR=..\data
set SCRIPT_SCHEMA=db_schema.sql
set SCRIPT_REF_TABLE=db_ref.sql
set BCGS_ROOT_20K=%DATA_DIR%\BCGS_20K\tiles
set BCGS_ROOT_2500K=%DATA_DIR%\BCGS_2500K\tiles

:: DB Table References
set TABLE_BCGS20KGrid=eclipse.BCGS20kGrid
set TABLE_BCGS2500KGrid=eclipse.BCGS2500kGrid

:: Create the database and tables
psql -h %HOST_NAME% -d %DB_NAME% -U %USERNAME% -f %SCRIPT_SCHEMA%

:: Populate the static reference tables
psql -h %HOST_NAME% -d %DB_NAME% -U %USERNAME% -f %SCRIPT_REF_TABLE%

:: Read and insert BCGS 20K tile geometry into reference tables
for %%F in (%BCGS_ROOT_20K%\*.shp) do (
    shp2pgsql -s %EPSG_WGS84% "%%F" %TABLE_BCGS20KGrid% | psql -h %HOST_NAME% -d %DB_NAME% -U %USERNAME%
)

:: Read and insert BCGS 2500K tile geometry into reference tables
for %%F in (%BCGS_ROOT_2500K%\*.shp) do (
    shp2pgsql -s %EPSG_WGS84% "%%F" %TABLE_BCGS2500KGrid% | psql -h %HOST_NAME% -d %DB_NAME% -U %USERNAME%
)

endlocal