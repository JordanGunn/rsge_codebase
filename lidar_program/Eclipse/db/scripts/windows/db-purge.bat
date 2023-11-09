@echo off
setlocal enabledelayedexpansion

REM Load your config and environment variables
call db-config.bat
call db-env.bat

set PATH_SQL_SCRIPTS=..\..
set SCRIPT_PURGE=%PATH_SQL_SCRIPTS%\eclipse_purge.sql

REM Run the SQL script
psql -h "%HOST_NAME%" -U "%USER_NAME%" -d "%DB_NAME%" -a -f "%SCRIPT_PURGE%"
