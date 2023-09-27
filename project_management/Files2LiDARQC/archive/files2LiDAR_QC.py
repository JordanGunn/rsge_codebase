# ============================ FUTURE IDEAS ====================================
# todo Prompt user if it is a BCTS Project (business areas) or not -- will make 
# todo it more complicated. =====

# todo Validation: delete any folders that were created in this process that 
# todo are empty (i.e., imagery for one UTM zone only, but multiple zones in proj)

# ==============================================================================

from tkinter import Tk
from tkinter import filedialog as Fd
import os
import shutil  # for copying/moving files
from ansi_colours import AnsiColors as colour  # imports the colour classes from separate py code
from osgeo import gdal  # for cog check
import re  # regex

root = Tk()
root.withdraw()

root.attributes('-topmost', True)

# * Prompts user for location to create folders, OR continue/skip to next step if
# * folders exist.

dir_path = Fd.askdirectory(
    title=(
        "Select contract directory to generate lidar QC Folders for projects without business areas "
    )
)

folder_list = [
    'Raster_Metadata',
    'Final_Coverage',
    'LiDAR_Metadata',
    'Imagery_Metadata'
]

for folder in folder_list:
    new_path = os.path.join(dir_path, folder)
    if not os.path.exists(new_path):
        os.mkdir(new_path)

# * Request for user input of utm zone numbers:
create_utm_folders = input(
    f'{colour.magenta}'
    f'Input all project UTM zones, separated by a single space: '
    f'{colour.green}'
)

user_zones = []
utm = "UTM"
utm_single_dig = "UTM0"

# * Adds the user-input zones into the list user_zones:
user_zones.extend(create_utm_folders.split(' '))

utm_list = []   # empty list for proper syntax of UTMXX folder

for i in user_zones:
    """
    Handles user input of UTM zones, so 'UTM' does not need to be included by the user,
    and single digits have a '0' prepended.
    """
    if len(i) == 2:
        utm_list.append(f'{utm}{i}')
        # inserts the string 'UTM' before the user-input zone (if 10 or higher)
    else:
        utm_list.append(f'{utm_single_dig}{i}')
        # inserts the string 'UTM' before the user-input zone (if 9 or lower)

# * Creates variables for LiDAR_QC root directories:
raster_meta_path = os.path.join(dir_path, folder_list[0])      # path of the raster_metadata folder
final_coverage_path = os.path.join(dir_path, folder_list[1])   # path of the final_coverage folder
lidar_meta_path = os.path.join(dir_path, folder_list[2])       # path of the LiDAR_Metadata folder
imagery_meta_path = os.path.join(dir_path, folder_list[3])     # path of the imagery_metadata folder

# * List of all sub folders to go into the sub UTM LiDAR_QC folders:

raster_sublist = ("DEM_COGs", "DSM_COGs")
lidar_sublist = ("Lasinfo", "Reports")
imagery_sublist = (
    "AT",
    "Airphoto_Metadata",
    "GSD_Report",
    "PatB",
    "Calibration",
    "Orthoimage_COGs"
)
coverage_sublist = ("LiDAR_Extents", "Ortho_Extents")

# ! ==============================IMPORTANT:=====================================
# ! 'folder_paths'
# and
# ! 'sub_folders_list' lists:
# Need to be in the correct order (i.e., raster_meta_path same index pos. as
# raster_sublist, etc.).AND list must currently remain the samelength, in order
# to use the zip() function infor-loop call of create_subs function.
# ! =============================================================================

folder_paths = (
    raster_meta_path,
    final_coverage_path,
    lidar_meta_path,
    imagery_meta_path
)
sub_folders_list = (
    raster_sublist,
    coverage_sublist,
    lidar_sublist,
    imagery_sublist
)


def create_subs(zones, folder_path, sub_folder):
    """
    Creates sub folders inside UTM sub folders for previously
    generated lidar QC server folders (folder_list)

    Args:
        zones (string): project UTM zone (e.g., UTM10)
        folder_path (string): parent folder path (e.g., LiDAR_Metadata)
        sub_folder (string): sub folder path (e.g., lasinfo)
    """
    utm_path = os.path.join(folder_path, zones)
    if not os.path.exists(utm_path):
        os.mkdir(utm_path)

    for f in sub_folder:
        sub_path = os.path.join(utm_path, f)
        if not os.path.exists(sub_path):
            os.mkdir(sub_path)


# * ask user if the project has imagery:
image_proj = input(f'{colour.magenta}Does this project have imagery? (Y/N) {colour.green}')

# * Removes any imagery metadata folders if no imagery in project (by user input):
if image_proj.upper() in ("N", "NO"):

    print(
        f'{colour.red}'
        f'No imagery in project, removing Imagery_Metadata and Ortho_Extents paths '
        f'{colour.reset}'
    )

    folder_paths = folder_paths[:3]          # removes the last index (imagery_meta_path)
    sub_folders_list = sub_folders_list[:3]  # removes the last index (imagery_sublist)
    coverage_sublist = ("LiDAR_Extents",)   # removes the ortho_extents folder from coverage_sublist

    # * re-writes 'sub_folders_list' with new coverage_sublist without imagery_extents:
    sub_folders_list = (raster_sublist, coverage_sublist, lidar_sublist, imagery_sublist)

    if os.path.exists(imagery_meta_path):
        os.rmdir(imagery_meta_path)

for zone in utm_list:
    for i, j in zip(folder_paths, sub_folders_list):
        create_subs(zone, i, j)

"""
in progress code below - working on generating regex strings to find specific metadata files and reports to then add to the appropriate folders automatically...
similar to files2lidarw script, moving to staging_folder; but the staging folder in this case is the lidar_QC server project folder (dir_path)

=============== Below is for adding data to empty root folders =================
================================================================================

use dir_path for output directory, and 'walk' through the appropriate
sub-folders, based on the file types below """


#* Raster file types as regex strings:
dem_cog = r'^(bc)_\d\d\d[A-Za-z]\d\d\d_x(li|l|r|rgb)(\dm|\dp\dm)_(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d\.tif$'
dsm_cog = r'^(bc)_\d\d\d[A-Za-z]\d\d\d_x(li|l|r|rgb)(\dm|\dp\dm)_(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d_(dsm|DSM)\.tif$'

raster_reglist = [
    dem_cog,
    dsm_cog
]

#* lidar metadata file types as regex strings:
lasinfo_file = r'(?i)^(bc)_\d\d\d[A-Za-z]\d\d\d_\d_\d_\d_xyes_\d_(utm08|utm09|utm10|utm11)_\d\d\d\d\.txt$'
lidar_metadata_report = r'(?i)^(op)\d\d(bmrs)\d\d\d_\d\d\d\d_(m|M)etadata\.pdf$'

lidar_meta_reglist = [
    lasinfo_file,
    lidar_metadata_report
]

#* Final coverage file types as regex strings:
lidar_extent = r'^(OP)\d\d(BMRS)\d\d\d_[A-Za-z]_(l|L)iDAR_(bcalb)\.shp$'
ortho_extent = r'^(OP)\d\d(BMRS)\d\d\d_[A-Za-z]_(o|O)rtho_(bcalb)\.shp$'

final_coverage_reglist = [
    lidar_extent,
    ortho_extent
]

#* Imagery metadata file types as regex strings: 
airphoto_meta = r'OP\d\dBMRS\d\d\d_\d\d\d\d_(AMF)_\d\d(bcd)\d\d\d\d\d\.xlsx$' # Verified
ortho_cogs = r'^bc_\d\d\d[A-Za-z]\d\d\d_(\d_\d_\d_xc|xc)\d\d\dmm_(utm08|utm09|utm10|utm11)_\d\d\d\d\.tif$' # Verified
gsd_report = r'OP\d\dBMRS\d\d\d_\d\d\d\d_GSD_(r|R)eporting\.xlsx$' # Verified
calibration_report = r'^OP\d\dBMRS\d\d\d_\d\d\d\d_(c|C)alib_(.*)\.pdf$' # Verified
manuf_calib_report = r'^OP\d\dBMRS\d\d\d_\d\d\d\d_(m|M)anuf_(c|C)alib_(.*)\.pdf$' # Verified
patB_file = r'OP\d\dBMRS\d\d\d_\d\d\d\d_(p|P)at(b|B)\.ori$' # Verified
georef_report = r'OP\d\dBMRS\d\d\d_\d\d\d\d_(g|G)eoref_(r|R)eport_((i|I)ndirect|(d|D)irect)\.pdf$' # Verified

imagery_meta_reglist = [
    airphoto_meta,
    ortho_cogs,
    gsd_report,
    calibration_report,
    manuf_calib_report,
    patB_file,
    georef_report
]

all_regex_lists = [
    raster_reglist,
    final_coverage_reglist,
    lidar_meta_reglist,
    imagery_meta_reglist,
]


def os_walk(path):
    """
    Uses os.walk to search through all folders of the "path"

    Args:
        path (string): root path of drive with data
    """
    for root, subDirs, files in os.walk(path):
        continue

def search_regex():
    """
    Looks for files on input drive (root) that match a regex string for metadata.
    Will eventually then copy those files to the appropriate created lidar QC
    server folder(s) (# Add stuff here). 
    """
    input_path = Fd.askdirectory("Input root of data drive: ")

    for reg_list in all_regex_lists:

        for single_regex in reg_list:
            if single_regex is dem_cog:
                print("Looking for DEM COGs... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )

            elif single_regex is dsm_cog:
                print("Looking for DSM COGs... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is lidar_extent:
                print("Looking for lidar Extent shapefile(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is ortho_extent:
                print("Looking for Ortho-image extent shapefile(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is lasinfo_file:
                print("Looking for lasinfo files... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is lidar_metadata_report:
                print("Looking for lidar metadata report(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is airphoto_meta:
                print("Looking for lidar metadata report(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )

            elif single_regex is ortho_cogs:
                print("Looking for Ortho-image COGs... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )

            elif single_regex is gsd_report:
                print("Looking for GSD Report(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )

            elif single_regex is calibration_report:
                print("Looking for In-situ camera calibration report(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )

            elif single_regex is manuf_calib_report:
                print("Looking for manufacturer camera calibration report... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
            
            elif single_regex is patB_file:
                print("Looking for PatB file(s)... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    # OR run the f'n copy_files()
                    shutil.copy(
                        #add stuff here
                    )
                        
            elif single_regex is georef_report:
                print("Looking for georeferencing report... ")
                search = re.search(single_regex, os_walk(input_path))
                if search is None:
                    print("None found! ")
                else:
                    shutil.copy(
                        #add stuff here
                    )


def copy_files():
    """
    _summary_
    """
    for root, subDirs, files in os.walk(dir_path):
        for folders in root:


        search_regex()
