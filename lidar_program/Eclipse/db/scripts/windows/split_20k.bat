@echo off
setlocal

:: Define input shapefile path, temporary file, output folder, and column name
set ROOT_20K="..\data\BCGS20K"
set INPUT_SHP="%ROOT_20K%\BCGS_20K_GRID\20K_GRID_polygon.shp"
set TILE_FLIST="..\data\BCGS_20K\tile_names_20k.txt"
set SHP_OUT_DIR="..\data\BCGS_20K\tiles"
set TILE_NAME_COL="MAP_TILE"

:: Extract unique tile names and save them to the temporary file
ogrinfo -al -geom=NO -q "%INPUT_SHP%" > "temp_all.txt"
findstr /R "%TILE_NAME_COL%" "temp_all.txt" > "temp_filtered.txt"
for /f "tokens=4 delims= " %%i in (temp_filtered.txt) do echo %%i >> %TILE_FLIST%
del temp_all.txt
del temp_filtered.txt

:: Loop over each unique tile name
for /f %%i in (%TILE_FLIST%) do (
    :: Create directory if it does not exist
    if not exist "%SHP_OUT_DIR%\%%i" mkdir "%SHP_OUT_DIR%\%%i"

    :: Extract tile and save to its folder
    ogr2ogr -where "%TILE_NAME_COL%='%%i'" "%SHP_OUT_DIR%\%%i\%%i.shp" %INPUT_SHP%
)

:: Remove temporary files
:: del %TILE_FLIST%

endlocal
