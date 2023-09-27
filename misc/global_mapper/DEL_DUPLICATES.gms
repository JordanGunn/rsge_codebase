// This Global Mapper script will load all LAZ files in from a directory (no subdirectories), remove the duplicate point records, and save the file to a specified output folder. 
// No need to change any paths in this script, simply run it from GM->File->Run Script

DEFINE_VAR NAME=dir PROMPT=DIR PROMPT_TEXT="Select folder of .laz files to remove duplicate points from"

DEFINE_VAR NAME=outdir PROMPT=DIR PROMPT_TEXT="Select output folder"

DIR_LOOP_START DIRECTORY=%dir% FILENAME_MASKS="*.laz" RECURSE_DIR=NO

	IMPORT FILENAME="%FNAME_W_DIR%"

	LIDAR_COMPARE DELETE_DUPLICATES=YES DUPLICATE_ATTR="INTENSITY" DUPLICATE_ATTR="GPS_TIME" DUPLICATE_ATTR="CLASS" DUPLICATE_ATTR="SOURCE_ID" DUPLICATE_ATTR="RETURN_NUM" DUPLICATE_ATTR="RETURN_CNT"


	EXPORT_VECTOR TYPE=LIDAR_LAS FILENAME="%outdir%%FNAME_WO_EXT%_dup_pnts_removed.laz" LAS_VERSION=1.4 GLOBAL_ENCODING=17 HEADER_OFFSET="0.0,0.0,0.0" HEADER_SCALE="0.01,0.01,0.01" INC_COLOR=NO


	UNLOAD_ALL
DIR_LOOP_END
