import os
import sys
import shutil
import subprocess
from glob import glob
from tkinter.filedialog import askdirectory


# TODO SET FILE PERMISSIONS OF SOURCE TO READ ONLY

IS_LINUX = (sys.platform == "linux") or (sys.platform == "linux2")

SHP_AUX = [
    ".shp",  # Main file containing geometry data
    ".shx",      # Shape index format
    ".dbf",      # Database format (contains attribute data for shapes)
    ".prj",      # Projection format (contains coordinate system information)
    ".sbn",      # Spatial index of features
    ".sbx",      # Spatial index of features
    ".fbn",      # Read-only spatial index of features
    ".fbx",      # Read-only spatial index of features
    ".ain",      # Attribute index of active fields in a table
    ".aih",      # Attribute index of active fields in a table
    ".ixs",      # Geocoding index for read-write shapefiles
    ".mxs",      # Geocoding index for read-write shapefiles (ODB format)
    ".atx",      # An attribute index for the .dbf file in the form of shapefilename.atx (ArcGIS 8 and later)
    ".shp.xml",  # Metadata (XML format)
    ".cpg"       # Character encoding format
]

VECTOR_FMT = [
    ".kml",
    ".kmz",
    ".gpkg",
    *SHP_AUX,
    ".csv"
]

# String Constants
SOURCE_FOLDERS_KEY = "source_folders"
FILE_EXTENSIONS_KEY = "file_extensions"

# Mapping dictionary
FOLDER_MAPPING = {

    "AUXILIARY": {
        "source_folders": [
            f"03_RIEGL_RAW{os.path.sep}02_RXP{os.path.sep}**",
            f"06_RIEGL_PROC{os.path.sep}07_RDB"
        ],
        "file_extensions": [".rxp", ".rdp"]
    },

    "COVERAGE": {
        "source_folders": [
            f"06_RIEGL_PROC{os.path.sep}09_EXPORT",
            f"06_RIEGL_PROC{os.path.sep}06_GEOIMAGES"
        ],
        "file_extensions": [*VECTOR_FMT]
    },

    "BASE_STATION": {
        "source_folders": [
            f"05_INS-GPS_PROC{os.path.sep}03_BASE"
        ],
        "file_extensions": [".rinex", ".RINEX", ".obs", ".OBS"]
    },

    "CONTROL": {
        "source_folders": [
            f"09_EXPORT"
        ],
        "file_extensions": [*VECTOR_FMT]
    },

    "RAW_LIDAR": {
        "source_folders": [
            f"06_RIEGL_PROC{os.path.sep}04_EXPORT"
        ],
        "file_extensions": [".laz", ".las"]
    },

    "IMU_GPS": {
        "source_folders": [
            f"05_INS-GPS_PROC{os.path.sep}01_POS",
            f"01_MON{os.path.sep}INS-GPS_1",
            f"02_FULL{os.path.sep}INS-GPS_1"
        ],
        "file_extensions": [".dat", ".imu", ".igs", ".out", ".raw"]
    }
    # Add more mappings as needed
}


def linux_shell_copy(src, dst):
    """
    Perform recursive copy using Linux shell-command.

    :param src: The source directory.
    :param dst: The destination Directory.
    """

    if not src.endswith('/'):
        src += '/'
    if not dst.endswith('/'):
        dst += '/'

    # Construct the rsync command
    cmd = [ 'rsync', '-a', '--include', '*/', '--exclude', '*', src, dst]

    # Execute the command
    subprocess.run(cmd, check=True)


def win_shell_copy(src, dst):

    """
    Perform recursive copy using Windows shell-command.

    :param src: The source directory.
    :param dst: The destination Directory.
    """

    cmd = ['robocopy', src, dst, '/E', '/XF', '*']

    # Execute the command
    subprocess.run(cmd, check=True)


def copy_folder_structure(src, dst) -> str:
    """
    Copies the folder structure from source to dest, excluding files.
    :param src: The source directory path.
    :param dst: The destination directory path.
    :return: The copied destination folder
    """

    # get the new copied destination
    head, root = os.path.split(src)
    dest_root = os.path.join(dst, root)
    os.makedirs(dest_root, exist_ok=True)
    linux_shell_copy(src, dest_root) \
        if IS_LINUX \
        else win_shell_copy(src, dest_root)

    return dest_root


def lp_ftree_json(path: str):
    """
    Generates a JSON representation of the folder structure for the given path.
    """
    tree = {}
    if os.path.isdir(path):
        for item in os.listdir(path):
            sub_path = os.path.join(path, item)
            if os.path.isdir(sub_path):
                tree[item] = lp_ftree_json(sub_path)
    return tree


def lp_copy(src: str, dst: str, ignore_folders: list = None):

    """
    Copy from the delivered source folder structure and translate
    into the GeoBC defined folder structure.

    Note that as of August 12, 2023, the folder structure of src
    is defined by the folder tree delivered by the currently contracted
    company responsible for acquisition

    :param src: Source root folder path.
    :param dst: Destination root folder path.
    :param ignore_folders: A list of extensions you wish to ignore (optional).
    """

    for folder in FOLDER_MAPPING.keys():

        if ignore_folders:
            ucase_folder = folder.upper()  # upper case folder name
            lcase_folder = folder.lower()  # lowercase folder name
            if (
                    lcase_folder in ignore_folders
            ) or (
                    ucase_folder in ignore_folders
            ):  # optional skip folder
                continue

        copy_files = []
        folder_dst = os.path.join(dst, folder)
        os.makedirs(folder_dst, exist_ok=True)
        sources = FOLDER_MAPPING[folder][SOURCE_FOLDERS_KEY]
        extensions = FOLDER_MAPPING[folder][FILE_EXTENSIONS_KEY]

        for source in sources:  # Gather files with desired extensions
            is_recursive = source.endswith("*")
            src_full = os.path.join(src, source)  # join the src root with current relative path
            files = []
            for ext in extensions:
                files.extend(
                    glob(os.path.join(src_full, "*" + ext), recursive=is_recursive)
                )
            if files:
                copy_files.extend(files)

        if copy_files:  # If files found with extensions, copy them to the GeoBC folder mappings
            for file in copy_files:
                shutil.copy(file, folder_dst)


def main():

    # Quick and dirty "GUI"
    src = askdirectory(title="Select the source ROOT directory (Copy from).")
    dst = askdirectory(title="Select the destination ROOT directory. (Copy to)")
    lp_copy(src, dst)


if __name__ == "__main__":
    main()
