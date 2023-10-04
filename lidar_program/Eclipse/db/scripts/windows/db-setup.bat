@echo off
setlocal enabledelayedexpansion

REM load config
call ".\db-config.bat"
call ".\db-env.bat"

REM DB Table References
set NAMESPACE=public
set TABLE_BCGS20K=%NAMESPACE%.BCGS20k
set TABLE_BCGS2500K=%NAMESPACE%.BCGS2500k

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
