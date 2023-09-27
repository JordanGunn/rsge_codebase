# -------------------------------------------------------------------------------------------
# COG tool creates cloud optimized geotiff for ortho, DEM, and DSM files
# Author: Olena Pylypenko
# Co-authors: Jordan Godau, Spencer Floyd
# -------------------------------------------------------------------------------------------
"""

This tool generates COGs for DEM, DSM and ortho files.

Takes root folder path (with source files) and output folder path as inputs.
Tool creates COG_output root folder in the provided output folder, with 3 folders inside: DSM, DEM and ortho.

After provided inputs popup window appears. It let to choose a COGs generation option. There are 3 options available:
DEM/DSM, ortho or for all the files.
Depending on the choice, tool will generate lists with files (based on the naming pattern for DSM, DEM and ortho files).
Lists then used in the COG generation functions. For every type of files there is a separate COG generation function.
Files in the provided list are filtered before COG generation:

    1)checks if there are COG files:
            - if yes - removes those from the list of files and lists them in the COG_generation_summary.txt,
            - is no - uses list of the same files for the next check

    2) compression check:
            ortho - required to be uncompressed
            DEM/DSM - should have LZW compression

            - if above conditions are not followed - COGs are still generated with a note added to the report
            about compression issues

At the end, empty output folders are removed, and COG_generation_summary.txt is created in the COG_outputs folder.


-------------------------            Important  note          ----------------------------------------------------------

Rules used to filter provided files in the cog_generation functions (ortho_cogs, dem_cogs, dsm_cogs):

1) IF all the files are already COGs - COGs won't be regenerated. COG_generation_summary will have a note about this.
2) IF all the files have incorrect compression requirements - COGs will still be generated. A note about compression
   issues will be added to the report.
3) IF there are source files that are COGs and some are not - COG files will be listed in the report. For not yet COGs -
   COGs will be generated.
4) IF no issues found with the source files - a note "Successfully generated (DEM|DSM|Ortho) COGs" will be added to the
   report.

"""

from pathlib import Path
import re
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import os
from osgeo import gdal
import shutil
import time
from datetime import date
from tqdm import tqdm
from glob import glob
from rsge_toolbox.raster.const_raster import RegexRaster, ImageFormats

gdal.UseExceptions()

# ---------------------------------------------------------------------------------------------------
# Code down below creates lists for DEM, DSM and ortho files using pattern of the file name
# ---------------------------------------------------------------------------------------------------

def ortho_files(all_flist):
    """

    Args:
        all_flist (): list of all the files found within root folder

    Returns: returns a list with ortho files

    """

    ortho_p = RegexRaster.FILENAME_ORTHO
    test = list()

    for file in all_flist:
        name = os.path.basename(file)
        if re.search(ortho_p, name):
            test.append(file)

    # removes duplicates from the generated test list
    ortho_l = [*set(test)]

    return ortho_l

def dsm_list(all_flist):
    """

    Args:
        all_flist (): list of all the files found within root folder

    Returns: returns a list with DSM files

    """

    dsm_p = RegexRaster.FILENAME_DSM
    test = list()

    for file in all_flist:
        name = os.path.basename(file)
        if re.search(dsm_p, name):
            test.append(file)

    # removes duplicates from the generated test list
    dsm_l = [*set(test)]

    return dsm_l

def dem_list(all_flist):
    """

    Args:
        all_flist (): list of all the files found within root folder

    Returns: returns a list with DEM files

    """

    dem_p = RegexRaster.FILENAME_DEM
    test = list()

    for file in all_flist:
        name = os.path.basename(file)
        if re.search(dem_p, name):
            test.append(file)

    # removes duplicates from the generated test list
    dem_l = [*set(test)]

    return dem_l

def all_files_list(root_folder):
    """
    Creates list of all the files found within the root folder with extensions -- .tif, tiff, geotif, geotiff

    Args:
        root_folder (): takes provided path to the root folder

    Returns:
         flist - list of all the files that meet required extensions: tif, tiff, geotif, geotiff

    """

    flist = list()

    # gets the absolute path for the root directory
    rootdir = os.path.abspath(root_folder)

    # looks for the files within root folder (including subfolders) and gives the list of all the tif, tiff, geotif, and geotiff files
    for dirpath, dirnames, filenames in os.walk(rootdir):
        tif_glob = os.path.join(dirpath, "*.tif")
        tiff_glob = os.path.join(dirpath, "*.tiff")
        gtif_glob = os.path.join(dirpath, "*.geotif")
        gtiff_glob = os.path.join(dirpath, "*.geotiff")

        tif_list = glob(tif_glob, recursive=True)
        tiff_list = glob(tiff_glob, recursive=True)
        gtif_list = glob(gtif_glob, recursive=True)
        gtiff_list = glob(gtiff_glob, recursive=True)

        flist.extend(tif_list)
        flist.extend(tiff_list)
        flist.extend(gtif_list)
        flist.extend(gtiff_list)

    # removes duplicates from the lists
    flist1 = [*set(flist)]

    return flist1

def dir_path_cog(destination_path):
    """
    Creates COG_output folder with 3 folders in it per file type: DSM, DEM and Ortho.

    Args:
        destination_path: folder where the resulting cog files will be placed

    Returns:
        dirpath_list - destination_dirpath. Includes path to DEM, DSM and Ortho output folders

    """
    dirpath_list = list()

    # assigns destination folder name
    destination_folder = 'COGs_outputs'

    # creates destination folder in the provided destination path
    path1 = os.path.join(destination_path, destination_folder)

    # checks if the COGs output folder already exists. Overwrites the existing folder if there is one
    if os.path.exists(path1):
        shutil.rmtree(path1)
        print("Overwrote the existing COGs folder")
    else:
        print("New COGs folder was created")

    # output folder path
    os.makedirs(path1)

    # creates 3 output folder in the destination COG_output folder
    for i in ["Ortho", "DSM", "DEM"]:
        path = os.path.join(path1, i)
        os.makedirs(path)
        dirpath_list.append(path)

    # removes duplicates from the lists
    dirpath_list1 = [*set(dirpath_list)]

    return dirpath_list1

def del_empty_output_folder(destination_path, pattern):
    """
    Args:
        destination_path (): path to the output folders for DEM, DSM and ortho files
        pattern (): "DSM", "DEM" or "ortho"

    Removes residual folders
    """

    for i in destination_path:
        if re.search(pattern, i):
            test_l = all_files_list(i)
            if len(test_l) == 0:
                shutil.rmtree(i)

# ---------------------------------------------------------------------------------------------------
# A few functions down below do cog_check and compression checks for the provided files.
# ---------------------------------------------------------------------------------------------------

def cog_check(list_of_files):
    """
    Checks if source files are already COGs

    Args:
        list_of_files (): accepts list with source files

    Returns: two lists with files:
            1) no_cog_ds1 - contains files that are not COGs
            2) cog_ds1 - contains files that are COGs

    """
    cog_ds = list()
    no_cog_ds = list()

    for image in list_of_files:
        img = gdal.Open(image, 0)
        metadata = img.GetMetadata("IMAGE_STRUCTURE")

        if "LAYOUT" in metadata:
            if metadata["LAYOUT"] == "COG":
                cog_ds.append(image)
        else:
            no_cog_ds.append(image)

    no_cog_ds1 = [*set(no_cog_ds)]
    cog_ds1 = [*set(cog_ds)]

    return no_cog_ds1, cog_ds1


def compression_check(file_list, pattern):
    """
    Checks if files have correct compression requirements.
    Ortho files should be not compressed.
    DEM/DSM files should have LZW compression.

    Args:
        file_list (): uses file list returned by the cog_check function
        pattern (): "dem/dsm" or "ortho" specifies the type of the files in the file_list

    Returns: two lists with files:
            1) correct_file_list - includes files that passed the requirements for files
            2) incorrect_file_list - includes files that do not have required parameters

    """
    correct_file_list = list()
    incorrect_file_list = list()

    for file in file_list:

        if pattern == 'dem/dsm':
            img = gdal.Open(file, 0)
            metadata = img.GetMetadata("IMAGE_STRUCTURE")

            if "COMPRESSION" in metadata:
                if metadata["COMPRESSION"] == 'LZW':
                    correct_file_list.append(file)
                else:
                    incorrect_file_list.append((file, metadata["COMPRESSION"]))
            img = None

        if pattern == 'ortho':
            img = gdal.Open(file, 0)
            metadata2 = img.GetMetadata("IMAGE_STRUCTURE")

            if "COMPRESSION" not in metadata2:
                correct_file_list.append(file)

            if "COMPRESSION" in metadata2:
                incorrect_file_list.append((file, metadata2["COMPRESSION"]))

            img = None

    return correct_file_list, incorrect_file_list


# ---------------------------------------------------------------------------------------------------
# A few functions down below generate COGs for ortho, DEM and DSM files
# ---------------------------------------------------------------------------------------------------

def create_cog(list_of_files, pattern, outpath):
    """
    Generates COG files using patterns to specify the file type (ortho|DSM|DEM) to apply correct parameters

    Args:
        list_of_files (): accepts list of files that should be converted to COGs
        pattern (): pattern specifies the file type
        outpath (): specifies the folder where generated COG files will be saved

    """

    for image in tqdm(list_of_files):

        img_name = os.path.basename(image)
        img1 = gdal.Open(image, 1)
        new_output = os.path.join(outpath, img_name)

        if re.search(pattern, r"ortho|Ortho|ORTHO"):
            gdal.Translate(new_output, img1,
                           options="-co BLOCKSIZE=512 -co NUM_THREADS=ALL_CPUS -co COMPRESS=JPEG -co QUALITY=95 -co OVERVIEWS=IGNORE_EXISTING -of COG ")

        if re.search(pattern, r"dem|DEM|DSM|dsm"):
            gdal.Translate(new_output, img1,
                           options="-co BLOCKSIZE=512 -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co OVERVIEWS=IGNORE_EXISTING -of COG ")

        img1 = None


def ortho_cogs(ortho_file_list, outpath):
    """
    Filters source files by the cog_check and compression_check functions.
    It generates COGs using file list returned by the cog_check function.
    Rules used to filter source files and generate COGs are described in the tool description.

    Args:
        ortho_file_list (): source file list returned by the ortho_files function
        outpath (): path to the destination folder for ortho files. Returned by the input_folders function.

    Returns: messages that added to the COG_generation_summary.txt

    """
    # chooses the correct output path to the ortho folder
    for path in outpath:
        ortho_dir_pattern = r"ortho|Ortho|ORTHO"
        if re.search(ortho_dir_pattern, str(path)):
            ortho_outpath = path

    # cog_check function checks if there are COGs in source files
    cog_check_output = cog_check(ortho_file_list)
    no_cog_ds = cog_check_output[0]
    cog_files = cog_check_output[1]

    # title txt block added to the COG_generation_summary
    msg1 = ""
    msg1 += "\n-----------------------------------------------------------------------------------------" + "\n"
    msg1 += "                               Ortho COG generation summary"
    msg1 += "\n-----------------------------------------------------------------------------------------"
    msg1 += "\n"

    # if provided list with files is not empty, it will move to the next filtration step
    if len(ortho_file_list) != 0:

        # checks compression type. Gives two output lists, first with correct files, second - with incorrect files.
        # referred as ortho_compress_check[0] and ortho_compress_check[1] in the code below
        ortho_compress_check = compression_check(no_cog_ds, 'ortho')

        # this condition is met if all the source files are COGs
        if len(no_cog_ds) == 0:
            msg1 += "\n" + str(len(cog_files)) + " is total number of files used for COG generation."
            msg1 += "\n"
            msg1 += "\nAll the ortho files are COGs."
            msg1 += "\nCOGs have not been regenerated for them." + "\n"

            return msg1

        # this condition is met if all the not cog files (var no_cog_ds) have incorrect compression
        elif len(ortho_compress_check[0]) == 0:
            msg1 += "\n" + str(len(no_cog_ds)) + " is total number of files used for COG generation."

            # creates a list with incorrect compression type(s)
            compression_types = list()
            for img in ortho_compress_check[1]:
                compression_types.append(img[1])

            # removes duplicates in the list
            compression_types1 = [*set(compression_types)]

            # creates comment about wrong compression type. Added to the report after COG generation is done
            if len(compression_types1) == 1 and len(ortho_compress_check[1]) == 1:
                msg1 += "\nThere is " + str(len(ortho_compress_check[1])) + " ortho file with " + compression_types1[
                    0] + " compression in the root folder found."
                msg1 += "\nThis file was used for COG generation regardless its compression type."
                msg1 += "\n"

            elif len(compression_types1) == 1 and len(ortho_compress_check[1]) > 1:
                msg1 += "\nThere are " + str(len(ortho_compress_check[1])) + " ortho files out of " + str(
                    len(no_cog_ds)) + " with " + compression_types1[0] + " compression in the root folder found."
                msg1 += "\nThese files were used for COG generation regardless their compression type."
                msg1 += "\n"

            else:
                compression_types1_str = str()
                for numb in range(len(compression_types1)):
                    if numb != (len(compression_types1) - 1):
                        compression_types1_str += compression_types1[numb]
                        compression_types1_str += ', '
                    else:
                        compression_types1_str += compression_types1[numb]

                msg1 += "\nThere are " + str(len(ortho_compress_check[1])) + " ortho files out of " + str(
                    len(no_cog_ds)) + " with " + compression_types1_str + " compression in the root folder found."
                msg1 += "\nThese files were used for COG generation regardless their compression type."
                msg1 += "\n"

            print("\nCreating COGs for ortho")
            # generates cogs from the source files
            create_cog(no_cog_ds, ortho_dir_pattern, ortho_outpath)
            return msg1

        # this condition is met if there are both, COG and not COG source files found
        elif len(no_cog_ds) > 0 and len(cog_files) > 0:
            msg1 += "\n" + str(len(no_cog_ds)) + " is total number of files used for COG generation."

            # create messages about source files that are COGs. Added to the report after COG generation is done
            if len(cog_files) == 1:
                msg1 += "\n"
                msg1 += "\nThis ortho file is already COG."
                msg1 += "\nIt has not been copied to the output COGs folder.There is no COG file regenerated for it:"

            else:
                msg1 += "\n"
                msg1 += "\nList of ortho files that are already COGs."
                msg1 += "\nThese files have not been copied to the output COGs folder. There are no COG files regenerated for them:"

            for cogs in cog_files:
                msg1 += ("\n" + str(cogs))

            msg1 += "\n"

            # Checks if there are files with correct and incorrect compression requirements
            if len(ortho_compress_check[0]) > 0 and len(ortho_compress_check[1]) > 0:
                msg1 += "\nOrtho files should have JPEG compression."

                # creates a list with incorrect compression type(s)
                compression_types = list()
                for img in ortho_compress_check[1]:
                    compression_types.append(img[1])

                # removes duplicates in the list
                compression_types1 = [*set(compression_types)]

                # creates a note about the compression issues. Added to the report after COG generation is done.
                if len(compression_types1) == 1 and len(ortho_compress_check[1]) == 1:

                    msg1 += "\nThere is " + str(len(ortho_compress_check[1])) + " ortho file with " + \
                            compression_types1[0] + " compression in the root folder found."
                    msg1 += "\nThis file was used for COG generation regardless its compression type."
                    msg1 += "\n"

                elif len(compression_types1) == 1 and len(ortho_compress_check[1]) > 1:
                    msg1 += "\nThere are " + str(len(ortho_compress_check[1])) + " ortho files out of " + str(
                        len(no_cog_ds)) + " with " + compression_types1[0] + " compression in the root folder found."
                    msg1 += "\nThese files were used for COG generation regardless their compression type."
                    msg1 += "\n"

                else:
                    compression_types1_str = str()
                    for numb in range(len(compression_types1)):
                        if numb != (len(compression_types1) - 1):
                            compression_types1_str += compression_types1[numb]
                            compression_types1_str += ', '
                        else:
                            compression_types1_str += compression_types1[numb]

                    msg1 += "\nThere are " + str(len(ortho_compress_check[1])) + " ortho files out of " + str(
                        len(no_cog_ds)) + " with " + compression_types1_str + " compression in the root folder found."
                    msg1 += "\nThese files were used for COG generation regardless their compression type."
                    msg1 += "\n"

                print("\nCreating COGs for ortho")
                # generates cogs from the output of the cog_check function
                create_cog(no_cog_ds, ortho_dir_pattern, ortho_outpath)

                return msg1

            # this condition is met if cog_check output files have correct compression
            else:

                if len(ortho_compress_check[0]) > 0 and len(ortho_compress_check[1]) == 0:
                    print("\nCreating COGs for ortho")
                    # generates cogs from the output of the cog_check function
                    create_cog(no_cog_ds, ortho_dir_pattern, ortho_outpath)

                    return msg1

        # this condition is met if there are no COG files among the source files
        else:
            msg1 += "\n" + str(len(no_cog_ds)) + " is total number of files used for COG generation."
            print("\nCreating COGs for ortho")
            # generates cogs from the output of the cog_check function
            create_cog(no_cog_ds, ortho_dir_pattern, ortho_outpath)

            msg1 += "\nSuccessfully generated ortho COGs\n"
            return msg1

    # if list with source files is empty the below message will be returned.
    else:

        msg1 += "\nThere are no ortho files found within the root folder suitable for COG generation." + "\n"
        return msg1


def dem_cogs(dem_l, outpath):
    """
    Filters source files by the cog_check and compression_check functions.
    It generates COGs using file list returned by the cog_check function.
    Rules used to filter source files and generate COGs are described in the tool description.

    Args:
        dem_l (): source file list returned by the dem_list function
        outpath (): path to the destination folder for DEM files. Returned by the input_folders function.

    Returns: messages that added to the COG_generation_summary.txt

    """
    # chooses the correct output path to the dem folder
    for path in outpath:

        dem_dir_pattern = r"dem|DEM"

        # title txt block added to the COG_generation_summary
        msg1 = ""
        msg1 += "\n-----------------------------------------------------------------------------------------" + "\n"
        msg1 += "                               DEM COG generation summary"
        msg1 += "\n-----------------------------------------------------------------------------------------"
        msg1 += "\n"

        # creates cogs for DEM and places them in the corresponding folder
        if re.search(dem_dir_pattern, str(path)):
            dem_outpath = path

            # cog_check function checks if there are COGs in source files
            cog_check_output = cog_check(dem_l)
            no_cog_dem = cog_check_output[0]
            cog_dem = cog_check_output[1]

            # if provided list with files is not empty, it will move to the next filtration step
            if len(dem_l) != 0:

                # checks compression type. Gives two output lists, first with correct files, second - with incorrect files.
                # referred as dem_compress_check[0] and dem_compress_check[1] in the code below
                dem_compress_check = compression_check(no_cog_dem, 'dem/dsm')

                # this condition is met if all the source files are COGs
                if len(no_cog_dem) == 0:
                    msg1 += "\n" + str(len(cog_dem)) + " is total number of files used for COG generation."
                    msg1 += "\nAll the DEM files are COGs."
                    msg1 += "\nCOGs have not been regenerated for them." + "\n"
                    return msg1

                # this condition is met if all the source files have incorrect compression
                elif len(dem_compress_check[0]) == 0:
                    msg1 += "\n" + str(len(no_cog_dem)) + " is total number of files used for COG generation."
                    # creates a list with incorrect compression type(s)
                    not_LZW_compression_types = list()
                    for img in dem_compress_check[1]:
                        not_LZW_compression_types.append(img[1])

                    # removes duplicates in the list
                    compression_types1 = [*set(not_LZW_compression_types)]

                    # creates comment about wrong compression type. Added to the report after COG generation is done
                    if len(compression_types1) == 1 and len(dem_compress_check[1]) == 1:
                        msg1 += "\nDEM files should have LZW compression."
                        msg1 += "\nThere is " + str(len(dem_compress_check[1])) + " DEM file with " + \
                                compression_types1[0] + " compression in the root folder found."
                        msg1 += "\nThis file was used for COG generation regardless its compression type."
                        msg1 += "\n"

                    elif len(compression_types1) == 1 and len(dem_compress_check[1]) > 1:
                        msg1 += "\nDEM files should have LZW compression."
                        msg1 += "\nThere are " + str(len(dem_compress_check[1])) + " DEM files out of " + str(
                            len(no_cog_dem)) + " with " + compression_types1[
                                    0] + " compression in the root folder found."
                        msg1 += "\nThese files were used for COG generation regardless their compression type."
                        msg1 += "\n"

                    else:
                        msg1 += "\nDEM files should have LZW compression."
                        compression_types1_str = str()
                        for numb in range(len(compression_types1)):
                            if numb != (len(compression_types1) - 1):
                                compression_types1_str += compression_types1[numb]
                                compression_types1_str += ', '
                            else:
                                compression_types1_str += compression_types1[numb]

                        msg1 += "\nThere are " + str(len(dem_compress_check[1])) + " DEM files out of " + str(
                            len(no_cog_dem)) + " with " + compression_types1_str + " compression in the root folder found."
                        msg1 += "\nThese files were used for COG generation regardless their compression type."
                        msg1 += "\n"

                    print("\nCreating COGs for DEM")
                    # generates cogs from the source files
                    create_cog(no_cog_dem, dem_dir_pattern, dem_outpath)

                    return msg1

                # this condition is met if there are both, COG and not COG source files found
                elif len(no_cog_dem) > 0 and len(cog_dem) > 0:
                    msg1 += "\n" + str(len(no_cog_dem)) + " is total number of files used for COG generation."
                    # create messages about source files that are COGs. Added to the report after COG generation is done
                    if len(cog_dem) == 1:
                        msg1 += "\n"
                        msg1 += "\nThis DEM file is already COG."
                        msg1 += "\nIt has not been copied to the output COGs folder:"

                    else:
                        msg1 += "\n"
                        msg1 += "\nList of DEM files that are already COGs"
                        msg1 += "\nThese files have not been copied to the output COGs folder:"

                    for cogs in cog_dem:
                        msg1 += ("\n" + str(cogs))

                    msg1 += "\n"

                    # Checks if there are files with correct and incorrect compression requirements
                    if len(dem_compress_check[0]) > 0 and len(dem_compress_check[1]) > 0:

                        # creates a list with incorrect compression type(s)
                        not_LZW_compression_types = list()
                        for img in dem_compress_check[1]:
                            not_LZW_compression_types.append(img[1])

                        # removes duplicates in the list
                        compression_types1 = [*set(not_LZW_compression_types)]

                        # creates a note about the compression issues. Added to the report after COG generation is done.
                        if len(compression_types1) == 1 and len(dem_compress_check[1]) == 1:
                            msg1 += "\nDEM files should have LZW compression."
                            msg1 += "\nThere is " + str(len(dem_compress_check[1])) + " DEM file with " + \
                                    compression_types1[0] + " compression in the root folder found."
                            msg1 += "\nThis file was used for COG generation regardless its compression type."
                            msg1 += "\n"

                        elif len(compression_types1) == 1 and len(dem_compress_check[1]) > 1:
                            msg1 += "\nDEM files should have LZW compression."
                            msg1 += "\nThere are " + str(len(dem_compress_check[1])) + " DEM files out of " + str(
                                len(no_cog_dem)) + " with " + compression_types1[
                                        0] + " compression in the root folder found."
                            msg1 += "\nThese files were used for COG generation regardless their compression type."
                            msg1 += "\n"

                        else:
                            msg1 += "\nDEM files should have LZW compression."
                            compression_types1_str = str()
                            for numb in range(len(compression_types1)):
                                if numb != (len(compression_types1) - 1):
                                    compression_types1_str += compression_types1[numb]
                                    compression_types1_str += ', '
                                else:
                                    compression_types1_str += compression_types1[numb]

                            msg1 += "\nThere are " + str(len(dem_compress_check[1])) + " DEM files out of " + str(
                                len(no_cog_dem)) + " with " + compression_types1_str + " compression in the root folder found."
                            msg1 += "\nThese files were used for COG generation regardless their compression type."
                            msg1 += "\n"

                        print("\nCreating COGs for DEM")
                        # generates cogs from the output of the cog_check function
                        create_cog(no_cog_dem, dem_dir_pattern, dem_outpath)
                        return msg1

                    # this condition is met if cog_check output files have correct compression
                    else:
                        if len(dem_compress_check[0]) > 0 and len(dem_compress_check[1]) == 0:
                            print("\nCreating COGs for DEM")
                            # generates cogs from the output of the cog_check function
                            create_cog(no_cog_dem, dem_dir_pattern, dem_outpath)
                            return msg1

                # this condition is met if there are no COG files among the source files
                else:
                    msg1 += "\n" + str(len(no_cog_dem)) + " is total number of files used for COG generation."

                    print("\nCreating COGs for DEM")
                    # generates cogs from the output of the cog_check function
                    create_cog(no_cog_dem, dem_dir_pattern, dem_outpath)

                    msg1 += "\nSuccessfully generated DEM COGs\n"
                    return msg1

            # if list with source files is empty the below message will be returned.
            else:

                msg1 += "\nThere are no DEM files found within the root folder suitable for COG generation." + "\n"
                return msg1


def dsm_cogs(dsm_l, outpath):
    """
        Filters source files by the cog_check and compression_check functions.
        It generates COGs using file list returned by the cog_check function.
        Rules used to filter source files and generate COGs are described in the tool description.

        Args:
            dsm_l (): source file list returned by the dsm_list function
            outpath (): path to the destination folder for DSM files. Returned by the input_folders function.

        Returns: messages that added to the COG_generation_summary.txt

        """
    # chooses the correct output path to the dsm folder
    for path in outpath:
        dsm_dir_pattern = r"dsm|DSM"

        # creates cogs for DSM and place them in the corresponding folder
        if re.search(dsm_dir_pattern, str(path)):
            dsm_outpath = path

            # title txt block added to the COG_generation_summary
            msg1 = ""
            msg1 += "\n-----------------------------------------------------------------------------------------" + "\n"
            msg1 += "                               DSM COG generation summary"
            msg1 += "\n-----------------------------------------------------------------------------------------"
            msg1 += "\n"

            # cog_check function checks if there are COGs in source files
            cog_dsm_all = cog_check(dsm_l)
            no_cog_dsm = cog_dsm_all[0]
            cog_dsm = cog_dsm_all[1]

            # if provided list with files is not empty, it will move to the next filtration step
            if len(dsm_l) != 0:

                # checks compression type. Gives two output lists, first with correct files, second - with incorrect files.
                # referred as dsm_compress_check[0] and dsm_compress_check[1] in the code below
                dsm_compress_check = compression_check(no_cog_dsm, 'dem/dsm')

                # this condition is met if all the source files are COGs
                if len(no_cog_dsm) == 0:
                    msg1 += "\n" + str(len(cog_dsm)) + " is total number of files used for COG generation."
                    msg1 += "\nAll the DSM files are COGs."
                    msg1 += "\nCOGs have not been regenerated for them." + "\n"
                    return msg1

                # this condition is met if all the source files have incorrect compression
                elif len(dsm_compress_check[0]) == 0:
                    msg1 += "\n" + str(len(no_cog_dsm)) + " is total number of files used for COG generation."
                    # creates a list with incorrect compression type(s)
                    not_LZW_compression_types = list()
                    for img in dsm_compress_check[1]:
                        not_LZW_compression_types.append(img[1])

                    # removes duplicates in the list
                    compression_types1 = [*set(not_LZW_compression_types)]

                    # creates comment about wrong compression type. Added to the report after COG generation is done
                    if len(compression_types1) == 1 and len(dsm_compress_check[1]) == 1:
                        msg1 += "\nDSM files should have LZW compression."
                        msg1 += "\nThere is " + str(len(dsm_compress_check[1])) + " DSM file with " + \
                                compression_types1[0] + " compression in the root folder found"
                        msg1 += "\nThis file was used for COG generation regardless its compression type."
                        msg1 += "\n"

                    elif len(compression_types1) == 1 and len(dsm_compress_check[1]) > 1:
                        msg1 += "\nDSM files should have LZW compression."
                        msg1 += "\nThere are " + str(len(dsm_compress_check[1])) + " DSM files out of " + str(
                            len(no_cog_dsm)) + " with " + compression_types1[
                                    0] + " compression in the root folder found."
                        msg1 += "\nThese files were used for COG generation regardless their compression type."
                        msg1 += "\n"

                    else:
                        msg1 += "\nDSM files should have LZW compression."
                        compression_types1_str = str()
                        for numb in range(len(compression_types1)):
                            if numb != (len(compression_types1) - 1):
                                compression_types1_str += compression_types1[numb]
                                compression_types1_str += ', '
                            else:
                                compression_types1_str += compression_types1[numb]

                        msg1 += "\nThere are " + str(len(dsm_compress_check[1])) + " DSM files out of " + str(
                            len(no_cog_dsm)) + " with " + compression_types1_str + " compression in the root folder found."
                        msg1 += "\nThese files were used for COG generation regardless their compression type."
                        msg1 += "\n"

                    print("\nCreating COGs for DSM")
                    # generates cogs from the output of the cog_check function
                    create_cog(no_cog_dsm, dsm_dir_pattern, dsm_outpath)

                    return msg1

                # this condition is met if there are both, COG and not COG source files found
                elif len(no_cog_dsm) > 0 and len(cog_dsm) > 0:
                    msg1 += "\n" + str(len(no_cog_dsm)) + " is total number of files used for COG generation."
                    # create messages about source files that are COGs. Added to the report after COG generation is done
                    if len(cog_dsm) == 1:
                        msg1 += "\n"
                        msg1 += "\nThis DSM file is already COG."
                        msg1 += "\nIt has not been copied to the output COGs folder:"

                    else:
                        msg1 += "\n"
                        msg1 += "\nList of DSM files that are already COGs."
                        msg1 += "\nThese files have not been copied to the output COGs folder:"

                    for cogs in cog_dsm:
                        msg1 += ("\n" + str(cogs))

                    msg1 += "\n"

                    # Checks if there are files with correct and incorrect compression requirements
                    if len(dsm_compress_check[0]) > 0 and len(dsm_compress_check[1]) > 0:

                        # creates a list with incorrect compression type(s)
                        not_LZW_compression_types = list()
                        for img in dsm_compress_check[1]:
                            not_LZW_compression_types.append(img[1])

                        # removes duplicates in the list
                        compression_types1 = [*set(not_LZW_compression_types)]

                        # creates a note about the compression issues. Added to the report after COG generation is done.
                        if len(compression_types1) == 1 and len(dsm_compress_check[1]) == 1:
                            msg1 += "\nDSM files should have LZW compression."
                            msg1 += "\nThere is " + str(len(dsm_compress_check[1])) + " DSM file with " + \
                                    compression_types1[0] + " compression in the root folder found."
                            msg1 += "\nThis file was used for COG generation regardless its compression type."
                            msg1 += "\n"

                        elif len(compression_types1) == 1 and len(dsm_compress_check[1]) > 1:
                            msg1 += "\nDSM files should have LZW compression."
                            msg1 += "\nThere are " + str(len(dsm_compress_check[1])) + " DSM files out of " + str(
                                len(no_cog_dsm)) + " with " + compression_types1[
                                        0] + " compression in the root folder found."
                            msg1 += "\nThese files were used for COG generation regardless their compression type."
                            msg1 += "\n"

                        else:
                            msg1 += "\nDSM files should have LZW compression."
                            compression_types1_str = str()
                            for numb in range(len(compression_types1)):
                                if numb != (len(compression_types1) - 1):
                                    compression_types1_str += compression_types1[numb]
                                    compression_types1_str += ', '
                                else:
                                    compression_types1_str += compression_types1[numb]

                            msg1 += "\nThere are " + str(len(dsm_compress_check[1])) + " DSM files out of " + str(
                                len(no_cog_dsm)) + " with " + compression_types1_str + " compression in the root folder found."
                            msg1 += "\nThese files were used for COG generation regardless their compression type."
                            msg1 += "\n"

                        print("\nCreating COGs for DSM")
                        # generates cogs from the output of the cog_check function
                        create_cog(no_cog_dsm, dsm_dir_pattern, dsm_outpath)

                        return msg1

                    # this condition is met if cog_check output files have correct compression
                    else:
                        if len(dsm_compress_check[0]) > 0 and len(dsm_compress_check[1]) == 0:
                            print("\nCreating COGs for DSM")
                            # generates cogs from the output of the cog_check function
                            create_cog(no_cog_dsm, dsm_dir_pattern, dsm_outpath)

                            return msg1

                # this condition is met if there are no COG files among the source files
                else:
                    msg1 += "\n" + str(len(no_cog_dsm)) + " is total number of files used for COG generation."
                    print("\nCreating COGs for DSM")
                    # generates cogs from the output of the cog_check function
                    create_cog(no_cog_dsm, dsm_dir_pattern, dsm_outpath)

                    msg1 += "\nSuccessfully generated DSM COGs" + "\n"
                    return msg1

            # if list with source files is empty the below message will be returned.
            else:

                msg1 += "\nThere are no DSM files found within the root folder suitable for COG generation" + "\n"
                return msg1

def select(option, file_lists: list[list], destination_dirpath: str):
    """
    Select function uses chosen option to generate COGs.
    Without it COG generation will be done for all the files automatically.

    Args:
        option (): this variable is received after submitting a choice on the popup window
        file_lists (): accepts lists with source files that are further assigned to the cog generation functions
        destination_dirpath (): list that stores all the destination path, returned by the input_folders function

    Returns:

    """
    # order of the lists stored in the file_list argument
    ortho_l = file_lists[0]
    dem_l = file_lists[1]
    dsm_l = file_lists[2]

    if option == "Create COGs for Ortho":
        return ortho_cogs(ortho_l, destination_dirpath)
    elif option == 'Create COGs for DEM / DSM':
        return dem_cogs(dem_l, destination_dirpath), dsm_cogs(dsm_l, destination_dirpath)
    else:
        if option == "Create COGs for all files":
            return ortho_cogs(ortho_l, destination_dirpath), dem_cogs(dem_l, destination_dirpath), dsm_cogs(dsm_l, destination_dirpath)

def popup_button():
    """
    Creates a popup window with COG generation options:
    1. COGs for ortho,
    2. COGs for DEM/DSM,
    3. COGs for all the files (ortho/DSM/DEM)

    Returns: an option for COG generation after Submit button is clicked

    """

    popup = Toplevel()
    cog_choice_var = str()

    # popup window with COG generation options
    while not cog_choice_var:

        popup.resizable(False, False)
        popup.grab_set()
        ttk.Label(popup, text='COG generation options').grid(row=0, column=0, padx=5, pady=5)
        chkb_frame = ttk.LabelFrame(popup, text='')
        chkb_frame.grid(row=1)

        cog_generation_options = {0: 'Create COGs for Ortho',
                                  1: 'Create COGs for DEM / DSM',
                                  2: "Create COGs for all files"}

        var = StringVar()

        # Create checkbuttons for tests
        row_num = 0
        column_num = 0
        for x in cog_generation_options.values():
            chkb = ttk.Radiobutton(chkb_frame, text=x, variable=var, value=x)
            if row_num >= 4:
                row_num = 0
                column_num = column_num + 2
            chkb.grid(row=row_num, column=column_num, sticky='W')
            row_num = row_num + 1

        button_frame = Frame(popup)
        button_frame.grid(row=2)
        is_submit_clicked = IntVar()

        ttk.Button(
            button_frame,
            text="Submit",
            command=lambda: is_submit_clicked.set(1)
        ).grid(pady=5)

        popup.wait_variable(is_submit_clicked)

        cog_choice_var = str(var.get())

        if len(cog_generation_options) == 0:
            messagebox.showerror(
                "Input error",
                "No options selected! Please select one COG generation option."
            )
        popup.destroy()
        popup.update()
    return cog_choice_var


def run(rootdir, output_folder):
    """
    Accepts two inputs

    Args:
        rootdir (): path to the source folder
        output_folder (): path to the output folder location

    """

    start_time = time.time()

    # List with path to the destination folders: dem, dsm and ortho
    destination_dirpath = dir_path_cog(output_folder)

    # List with path to the source folders
    file_list = all_files_list(rootdir)

    # COG generation summary
    msg = ""
    srctextfile = open((str(output_folder + "\COGs_outputs") + "\COG_generation_summary_" + str(date.today()) + ".txt"),'a')

    msg += "COG generation summary" + "\n"
    msg += "\n"
    msg += "Start time: " + str(date.today()) + " " + str(time.strftime("%H:%M:%S")) + "\n"

    # lists with source files for dem, dsm and ortho
    ortho_l = ortho_files(file_list)
    dem_l = dem_list(file_list)
    dsm_l = dsm_list(file_list)

    # list used in the select function.
    # Do not change the order of lists in it, or change it in the source function too
    lists = [ortho_l, dem_l, dsm_l]

    # COG generation choice passed from the popup window
    cog_choice_var = popup_button()

    # list that includes multimple messages returned from the different cog generation function
    msg1 = list()

    # select function processing the cog generation option based on the cog_choice_var
    msg1 = select(cog_choice_var, lists, destination_dirpath)

    # copies all the messages received from the 'select' function above and adds them to the msg
    try:
        if len(msg1) > 0:
            for i in msg1:
                if type(i) is str:
                    msg += i
                if type(i) is tuple:
                    for j in i:
                        msg += j
        else:
            msg += msg1

    except TypeError:
        pass

    # removes empty output folders at the end
    del_empty_output_folder(destination_dirpath, r"ortho|ORTHO|Ortho")
    del_empty_output_folder(destination_dirpath, r"dsm|DSM")
    del_empty_output_folder(destination_dirpath, r"dem|DEM")

    total_time = time.time() - start_time

    msg += "\n-----------------------------------------------------------------------------------------" + "\n"
    msg += f'\nCOGs generation run time  - {time.strftime("%H:%M:%S", time.gmtime(total_time))}'

    print(msg, file=srctextfile)
    srctextfile.close()

    print("\nFind the COG_summary_generation.txt file in the provided output folder.")


def main():
    # rootdir = None
    # output_folder = None

    """

    """
    # closes small annoying tkinter window that starts automatically if tkinter used in the code
    Tk().withdraw()

    rootdir = Path(filedialog.askdirectory(title="Select directory containing files"))
    output_folder = (filedialog.askdirectory(title="Select output directory"))

    run(rootdir, output_folder)


if __name__ == "__main__":
    main()
