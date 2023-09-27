from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from tkinter import filedialog
import os
import glob
import math
from pathlib import Path
from tqdm import tqdm
import re
import cv2
from statistics import mean

"""
Created by Spencer Floyd

**** All parent 3 band rgb .tif files and it's corresponding .jpg thumbnail need to be in the same input root location. In other words,
    both .tif and .jpg files must be within the root (or subdirectory) of the input path****
    
Compares pixel height and width of thumbnail and its original .tif image.
Checks to see if there is a thumbail for every raw image.
Finds all thumbnails that are not 1/16 the size of its original image based on pixel width and height with a tolerance of 1 pixel.
Iterates through each row and column of thumbnails and raises error if any are all black or all white

"""

def run_from_gui(inDir,outDir):
    """
    Runs script when exicuted by ORIQCS

    Args:
        inDir (str): root directory containing thumbnails and parent TIF images
        outDir (str): directory where output will go

    Returns:
        thumbnail_report (.txt)

    """
    def get_thumb_width(filepath):
        width = Image.open(filepath).width
        return width

    def get_thumb_height(filepath):
        height = Image.open(filepath).height
        return height

    def get_tif_width(filepath):
        width = Image.open(filepath).width
        return width

    def get_tif_height(filepath):
        height = Image.open(filepath).height
        return height

    # Delete previously created 'thumbnails_report.txt'
    for filename in glob.glob(outDir+r"\thumbnail_report*"):
        os.remove(filename)

    # Create empty/null variables
    thumb_list = []
    tif_list = []
    tif_dim = []
    thumb_dim = []
    thumb_error_list = []
    thumb_count_list = []
    tif_count_list = []
    thumb_dim_error_list = []
    thumb_error_count = 0
    incorrect_thumb_count = 0
    pre_thumb_count = 0
    pre_tif_count = 0
    thumb_count = 0

    # regex
    re_thumb = r'^\d\d(bcd|BCD).*(jpg|jpeg|JPG|JPEG)$'
    re_tif = r'^\d\d(bcd|BCD).*8bit_rgb\.(tif|tiff|TIF|TIFF)$'

    # Loop through Thumb directory and get name, height, width of each thumb
    for root, subFolder, files in (os.walk(inDir)):
        for file in files:
            if re.search(re_thumb, file):
                pre_thumb_count += 1
                f = os.path.join(root, file)
                thumb_width = get_thumb_width(f)
                thumb_height = get_thumb_height(f)
                file_name = Path(f).stem
                f_name = (file_name[0:14])
                thumb_count_list.append(f_name)
                thumb_list += [[f_name, thumb_width, thumb_height]]
            else: continue

    # Loop through TIF directory and get name, height, width of each tif
    for root, subFolder, files in (os.walk(inDir)):
        for file in files:
            if re.search(re_tif, file):
                pre_tif_count +=1
                f = os.path.join(root, file)
                tif_width = get_tif_width(f)
                tif_height = get_tif_height(f)
                file_name = Path(f).stem
                f_name = (file_name[0:14])
                print (f_name)
                tif_count_list.append(f_name)
                tif_list += [[f_name, tif_width, tif_height]]
                height_dimension = round(tif_height/16)
                width_dimension = round(tif_width/16)
                tif_dim.append(str(width_dimension) + " X " + str(height_dimension))
            else: continue

    # Create a list of dimensions based on TIF files without duplicates
    tif_dim_set = set(tif_dim)
    tif_dim_list = list(tif_dim_set)

    # Create thumbnail_report
    with open(outDir + "/thumbnail_report.txt", "a") as thumb_report:
        thumb_report.write(f"Thumbnail Report\n\n")
        thumb_report.write(f"Correct thumbnail dimensions based on TIF images: {tif_dim_list}\n\n")
        thumb_report.write(f"{pre_tif_count} TIF images in this project\n\n\n")
        if pre_thumb_count != pre_tif_count:
            missing_image_count = abs(pre_thumb_count-pre_tif_count)
            missing_images = list(set(tif_count_list)- set(thumb_count_list))
            thumb_report.write(f"MISSING THUMBNAIL ERROR \n{missing_image_count} TIF image(s) are missing thumbnails\n\n")
            for e in missing_images:  
                thumb_report.write(f"{e}.tif\n")
            thumb_report.write(f"\n\n")
    
    # Loop through thumbs and compare each with its parent .tif image
    for thumb in thumb_list:
        for tif in tif_list:
            if thumb[0] == tif[0]:
                thumb_count += 1
                thumb_width = thumb[1]
                thumb_height = thumb[2]
                tif_width_ratio = tif[1]/16
                tif_height_ratio = tif[2]/16
                tif_width_ratio_upper_tolerance = math.ceil(tif_width_ratio)
                tif_width_ratio_lower_tolerance = math.floor(tif_width_ratio)
                tif_height_ratio_upper_tolerance = math.ceil(tif_height_ratio)
                tif_height_ratio_lower_tolerance = math.floor(tif_height_ratio)
                if tif_width_ratio_lower_tolerance <= thumb_width <= tif_width_ratio_upper_tolerance and tif_height_ratio_lower_tolerance <= thumb_height <= tif_height_ratio_upper_tolerance:
                    continue
                else:
                    incorrect_thumb_count += 1
                    thumb_dim_error_list.append(thumb[0])
                    thumb_dim.append(str(thumb_width) + " X " + str(thumb_height))
                    thumb_dim_set = set(thumb_dim)
                    thumb_dim_list = list(thumb_dim_set)
    if incorrect_thumb_count >0:
        with open(outDir + "/thumbnail_report.txt", "a") as thumb_report:
            thumb_report.write(f"DIMENSION ERROR\n{incorrect_thumb_count} thumbnails have incorrect dimensions of: {thumb_dim_list}\n\n")
            for e in thumb_dim_error_list:
                thumb_report.write(f"{e}.jpg\n")
            thumb_report.write(f"\n\n")

    # Loop through Thumb directory and check for images with all white/black columns/rows
    for root, subFolder, files in os.walk(inDir):
        for file in tqdm(files, desc="Checking thumbnail files for row errors"):
            if re.search(re_thumb, file):
                f = os.path.join(root, file)
                img = cv2.imread(f)
                rows = img.shape[0]

                for i in range(rows):
                    band1_row = mean(img[i,:,0])
                    band2_row = mean(img[i,:,1])
                    band3_row = mean(img[i,:,2])
                    if band1_row == band2_row == band3_row:
                        thumb_error_list.append(str(file))
                        thumb_error_count += 1
                        break
                    else: 
                        continue
            
            # Create a list of thumbnail error files without duplicates
            thumb_error_set = set(thumb_error_list)
            thumb_error_list = list(thumb_error_set)

        if thumb_error_count > 0:
            with open(outDir + "/thumbnail_report.txt", "a") as thumb_report:
                thumb_report.write(f"THUMB ROW ERROR\nThe following image(s) contain one or more rows that are the same colour (possibly corrupt) :\n\n")
                for e in thumb_error_list:
                    thumb_report.write(f"{e}\n")
                thumb_report.write(f"\n\n")
                break

def main():
    inDir = filedialog.askdirectory(title="Select input directory")
    outDir = filedialog.askdirectory(title="Select output directory")
    run_from_gui(inDir, outDir)

if __name__ == '__main__':
    main()