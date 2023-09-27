// This Global Mapper script will load all LAZ files in from a directory (no subdirectories), remove the duplicate point records, and save the file to a specified output folder. 
// No need to change any paths in this script, simply run it from GM->File->Run Script

DEFINE_VAR NAME=dir PROMPT=DIR PROMPT_TEXT="Select input .laz folder"

DEFINE_VAR NAME=outdir PROMPT=DIR PROMPT_TEXT="Select output folder"

DIR_LOOP_START DIRECTORY=%dir% FILENAME_MASKS="*.laz" RECURSE_DIR=NO

	IMPORT FILENAME="%FNAME_W_DIR%"

	GENERATE_ELEV_GRID FILENAME="%FNAME_W_DIR%" GRID_ALG="BIN_AVG" SPATIAL_RES_METERS="0.5" GRID_TYPE="INTENSITY" CREATE_IMAGE=YES


	EXPORT_RASTER TYPE=GEOTIFF FILENAME="%outdir%%FNAME_WO_EXT%.tif" COMPRESSION=LZW


	UNLOAD_ALL
DIR_LOOP_END
