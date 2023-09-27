# Created by Spencer Floyd and Natalie Jackson
# Organizes and copies lidar, DEM, Ortho, and DSM files to Lidar Accessw network drive

import os, glob
from osgeo import gdal
import shutil
import tkinter as tk
import re
import getpass
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tqdm import tqdm
from datetime import datetime
import csv
# Creates GUI

root = tk.Tk()
root.iconbitmap(r"Z:\SPENCER_FLOYD\.ico\bc_logo.ico")
root.title("Files > Accessw")
root.geometry("290x250")
root.configure(bg="#9EB1CE")
root.eval('tk::PlaceWindow . center')
label = Label(root, text="Fill in Contract Number", bg="#9EB1CE")
label.pack()

# Creates global variables

date = datetime.now().strftime("%Y_%m_%d")
top_common_path = r"Z:\LiDAR_AccessW_Copy_History"
csv_filepath = r"Z:\LiDAR_AccessW_Copy_History\LiDAR_AccessW_Copy_History.csv"
lapath = r"U:"
user = getpass.getuser()
not_COG = 0
files_copied = 0

# Creates first pop up with instructions and a warning about overwrite

messagebox.showinfo("Copy Files to lidar Accessw Drive", "After you click OK, you will be prompted to select a working directory. Ensure this directory has enough free space to populate and organize all the files you will be moving to lidar AccessW.\n\n\
*Your working directory must not be in the same directory as the files you wish to move*\n\n\
In the directory you choose, a folder will be created named Staging_Folder. The Staging_Folder is where all files will be populated and organized before being moved to the lidar Accessw Drive.\n\n\
If a folder is named Staging_Folder in the directory you choose, it will be OVERWRITTEN")

# Prompts user for working directory and creates folder called "Staging_Folder"

workspace = filedialog.askdirectory(title="Select Staging Directory")
os.chdir(workspace)
Staging_Folder = "Staging_Folder"
destpath = workspace +"/Staging_Folder"
if os.path.exists(destpath):
    shutil.rmtree(destpath)
os.makedirs(destpath)

# Prompts user for the root directory where the files they wish to copy to lidar AccessW exist

messagebox.showinfo("Select Root Directory Where Files Exist", "Select the root directory within which all the files you wish to copy exist.")

srcpath = filedialog.askdirectory(title="Select Root Directory Of The Files You Wish To Copy.")

# Checkbox variables

lidar_check = IntVar()
ortho_check = IntVar()
dem_check = IntVar()
dsm_check = IntVar()

# Entry box

entry = Entry(root,justify = 'center', width = 20, borderwidth= 4)
entry.place(x=80,y=22)

# Entry box function

def submit():
    contract = entry.get()
    print ("Contract number " + contract + " submitted\n")
    return str(contract)

# Contract variable

con_string = submit()

# Data types function

def _data_types():
    data_types = (
        "lidar",
        "ortho",
        "dem",
        "dsm"
    )

    return data_types


def copy_data_type(type):
    
    data_types = _data_types()

    if type == data_types[0]:
        progress_message = "lidar Copying"
        regex_string = r'^(B|b)(C|c)_\d\d\d[A-Za-z]\d\d\d_\d_\d_\d_xyes_(\d|\d\d)_(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d.laz$'
        out_folder_suffix = "pointcloud"
        type_get = (lidar_check.get())
        file_type = "pointcloud"

    elif type == "ortho":
        progress_message = "Ortho Copying "
        regex_string = r'^(B|b)(C|c)_\d\d\d[A-Za-z]\d\d\d_(\d_\d_\d_xc|xc)\d\d\dmm_(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d.tif$'
        out_folder_suffix = "orthophoto"
        type_get = (ortho_check.get())
        file_type = "orthophoto"

    elif type == "dem":
        progress_message = "DEM Copying "
        regex_string = r'^(B|b)(C|c)_\d\d\d[A-Za-z]\d\d\d_x(li|l|r|rgb)(\dm|\dp\dm)_(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d.tif$'
        out_folder_suffix = "dem"
        type_get = (dem_check.get())
        file_type = "dem"
        
    elif type == "dsm":
        progress_message = "DSM Copying "
        regex_string = r'(utm08|UTM08|utm8|UTM8|utm09|UTM09|utm9|UTM9|utm10|UTM10|utm11|UTM11)_\d\d\d\d_(dsm|DSM).tif$'
        out_folder_suffix = "dsm"
        type_get = (dsm_check.get())
        file_type = "dsm"

    if type_get == 1:
        for root, subFolder, files in (os.walk(srcpath)):
            count = 0
            length = len(files)
            for file in files:
                count += 1
                global not_COG
                global files_copied
                var2 = "%     "
                re_tile = re.search(r'\d+|$',file)
                re_tile_letter = re.search(r'\d{3}[a-zA-Z]+|$',file)
                re_year = re.search(r'\d{4}',file)
                print (progress_message,int(count/length*100),var2, end='\r')
                if re.search(regex_string, file):
                    if not file_type == "pointcloud":
                        is_cog = cog_check(os.path.join(root,file))
                        if is_cog:
                            subFolder = os.path.join(destpath, (re_tile.group()), (re_tile_letter.group()), (re_year.group()), file_type)
                            if not os.path.isdir(subFolder):
                                os.makedirs(subFolder)
                            if re.search(regex_string, file):
                                files_copied +=1
                                shutil.copy(os.path.join(root, file), subFolder)
                                os.rename((subFolder + os.sep + file), (subFolder + os.sep + file.lower()))
                                with open(destpath+r"\Files_Copied_To_Staging_Folder.txt","a") as files_copied_text:
                                    files_copied_text.write(root + os.sep + file+ "\n")
                        else:
                            not_COG += 1
                            with open(destpath+r"\Non_COG_Geotiffs_Skipped.txt","a") as not_COG_text:
                                not_COG_text.write(root + os.sep + file+ "\n")
                    else:
                        subFolder = os.path.join(destpath, (re_tile.group()), (re_tile_letter.group()), (re_year.group()), file_type)
                        if not os.path.isdir(subFolder):
                                os.makedirs(subFolder)
                        if re.search(regex_string, file):
                            files_copied +=1
                            shutil.copy(os.path.join(root, file), subFolder)
                            os.rename((subFolder + os.sep + file), (subFolder + os.sep + file.lower()))
                            with open(destpath+r"\Files_Copied_To_Staging_Folder.txt","a") as files_copied_text:
                                files_copied_text.write(root + os.sep + file+ "\n")
                continue
        for root, subFolder, files in (os.walk(destpath)):
            for folder in subFolder:
                if folder.endswith(file_type):
                    os.rename((root + os.sep + folder ), ((root + os.sep + out_folder_suffix)))

def cog_check(input_raster):

    ds = gdal.Open (input_raster,0)

    metadata = ds.GetMetadata("IMAGE_STRUCTURE")

    if "LAYOUT" in metadata:
        if metadata ["LAYOUT"]=="COG":
            is_cog = True
        else:
            is_cog = False
    else:
        is_cog = False
    return is_cog
    
def copy_files():

# Copy Files

    data_types = _data_types()

    for data_type in data_types:
        copy_data_type(data_type)

    if not_COG >0:

        print ("In total,"+ str(files_copied) + "  files were copied to Staging_Folder. See 'Files_Copied_To_Staging_Folder' in Staging_Folder. \n\n "+ str(not_COG)  +" Geotiffs did not pass the COG check and were not copied. This may not be problem if both the COGs and their original non-COG file exist in the same root directory. Check 'Non_COG-Geotiffs_Skipped.txt' file in the staging folder for the list of files skipped.")

        messagebox.showinfo("", "In total, "+ str(files_copied) + "  files were copied to Staging_Folder. See 'Files_Copied_To_Staging_Folder' in Staging_Folder.")

        messagebox.showinfo("WARNING", str(not_COG) + "  Geotiffs did not pass the COG check and were not copied. This may not be problem if both the COGs and their original non-COG file exist in the same root directory. Check 'Non_COG-Geotiffs_Skipped.txt' file in the staging folder for the list of files skipped.")

    else:

        print ("In total,"+ str(files_copied) + "  files were copied to Staging_Folder. See 'Files_Copied_To_Staging_Folder' in Staging_Folder. \n\n ")

        messagebox.showinfo("", "In total, "+ str(files_copied) + "  files were copied to Staging_Folder. See 'Files_Copied_To_Staging_Folder' in Staging_Folder.")
    
# Checks for duplicate files between Staging_Folder and lidar Accessw Drive and creates a .txt of all duplicate files as well as a list of all files present in Staging_Folder

def check_for_duplicates():
    for filename in glob.glob(destpath+"/Files_Copied_To_Staging_Folder*"):
        os.remove(filename)
    for filename in glob.glob(destpath+"/Non_COG_Geotiffs_Skipped*"):
        os.remove(filename)
    duplicates_list = 0
    count = 0
    length = sum([len(files) for root, directory, files in os.walk(destpath)])
    source_files = list()
    for (dirpath, dirnames, filenames) in (os.walk(destpath)):
        source_files += [os.path.join(file) for file in filenames]
        for file in filenames:
            count += 1
            var1 = "Creating list of files in Staging_Folder "
            var2 = "%    "
            print (var1,int(count/length*100),var2, end='\r')
    
    lidar_accessw_files = list()
    count = 0
    length = sum([len(files) for root, directory, files in os.walk(lapath)])
    for (dirpath, dirnames, filenames) in (os.walk(lapath)):
        lidar_accessw_files += [os.path.join(file) for file in filenames]
        for file in filenames:
            count += 1
            var1 = "Creating list of files in lidar Accessw "
            var2 = "%     "
            print (var1,int(count/length*100),var2, end='\r')
        
    srctextfile = open(destpath+"\Staging_Folder_File_List_"+date+".txt", "a")
    print ("\n\nCreating text file list of Staging_Folder files")
    for element in tqdm(source_files):
        srctextfile.write(element + "\n")
    srctextfile.close
        
    dup = set(source_files).intersection(lidar_accessw_files)
    duptext = open(destpath +"\Pre_Copy_Duplicate_File_List_"+date+".txt", "a")
    print ("\n\nChecking for duplicates")
    for element in tqdm(dup):
        duplicates_list +=1
        duptext.write(element + "\n")
    duptext.close
    print ("\n\nDuplicate check complete\n\nThere are " + str(duplicates_list) + " file(s) in your Staging_Folder that share the same name as other file(s) on lidar AccessW.\n\nCheck Staging_Folder for text files\n")
    messagebox.showinfo("", "There are " + str(duplicates_list) + " file(s) in your Staging_Folder that share the same name as other file(s) on lidar AccessW.\nCheck Staging_Folder for text files")
    
# Copys Staging_Folder contents to lidar Accessw Drive and deletes .txt files from Staging_Folder before copy

def copy_to_lidar_drive():
    con_string = submit()
    count = 0
    length = sum([len(files) for root, directory, files in os.walk(destpath)])
    for filename in glob.glob(destpath+"/Pre_Copy*"):
        os.remove(filename)
    for filename in glob.glob(destpath+"/Staging_Folder_File*"):
        os.remove(filename)
    for filename in glob.glob(destpath+"/Duplicate_Files_Not*"):
        os.remove(filename)
    for filename in glob.glob(destpath+"/Files_Copied*"):
        os.remove(filename)

    count_files_not_moved = 0
    
    for src_dir, dirs, files in os.walk(destpath):
        dst_dir = src_dir.replace(destpath, lapath, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file in files:
            count += 1
            var1 = "Files being moved to lidar AccessW "
            var2 = "%"
            print (var1,int(count/length*100),var2, end='\r')
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            if os.path.exists(dst_file):
                count_files_not_moved +=1
                with open(destpath+"\Duplicate_Files_Not_Moved_"+date+".txt", "a") as duplicate_report:
                    duplicate_report.write(src_dir + os.sep + file+ "\n")
            else:
                with open(top_common_path+"\Files_Copied_" + date + "_" + user + "_" + con_string + ".txt", "a") as move_report:
                    move_report.write(file+ "\n")
                shutil.move(src_file, dst_dir)
                csv_writer = csv.writer(open(csv_filepath, mode="a", newline=""))
                csv_writer.writerow([file, con_string])

    if count_files_not_moved < 1:
        print("\n\nAll files were moved from the Staging_Folder to the lidar Accessw Drive", flush=True)
        messagebox.showinfo("", "All files were moved from the Staging_Folder to the lidar Accessw Drive")
    else:
        print("\n\nWARNING " + str(count_files_not_moved) + " FILES WERE NOT MOVED TO LIDAR ACCESSW DRIVE\n\
See 'Duplicate_Files_Not_Moved.txt' in Staging_Folder for files that were skipped because they share the same name as another file on the lidar Accessw Drive")
        messagebox.showinfo("",str(count_files_not_moved) + " FILES WERE NOT MOVED TO LIDAR ACCESSW DRIVE\n\
See 'Duplicate_Files_Not_Moved.txt' in Staging_Folder for files that were skipped because they share the same name as another file on the lidar Accessw Drive")

# Creates instruction button instructions

def instructions():
    messagebox.showinfo("Instructions","This program organizes and moves data to the lidar Accessw network drive\n\n\
    SET UP\n\n\
    When you opened this program, it prompted you for a working directory. This directory must have enough space to contain all the files you want to move to the lidar Accessw Drive.\
    The directory you chose will now have an empty folder called Staging_Folder. This is where all the files will be copied and organized based on tile number, year, and file type.\
    \n\n Start by filling in the contract number and submitting it using the submit button. Next, check the file types you would like to copy by checking the corresponding checkbox.\n\n\
    1. Copy Files - This button will prompt you for the drive or root folder containing all files you wish to copy. It will only copy COGs and .laz files.\
    This will look through all subfolders within the drive or root folder you selected and copy all files from those folders to the\
    Staging_Folder where the apropriate folders will be created and populated by the copied files.\n\n\
    2. Check for Duplicate Files - This will make a list of all the files within the Staging_Folder as well as a list of all the files in the Lidar Accessw drive.\
    These lists are compared, and if any duplicate names are found, they will be found in the Pre_Copy_Duplicate_fileList.txt created in the Staging_Folder.\
    If duplicates exist, they will need to be dealt with on a file to file basis.\n\n\
    3. Move to lidar Accessw - This will move all files (that don't already exist on Lidar Accessw) from the Staging_Folder to the Lidar Accessw drive. After they are copied, a pop up will tell you if all the files\
    were moved successfully, or if one or more files were skipped because duplicates were not dealt with pre move. If duplicates still exist, look at the Duplicate_Files_Not_Copied.txt file\
    created in the Staging_Folder. A text file list of all files copied is created on Top_Common in the folder 'LiDAR_AccessW_Copy_History'. If more than one batch of files is copied on the same day, the initial text\
    file will be appended to the text file list of that day.\
    If all files copied successfully, you may rejoice and high five the nearest human, but then immediately get back to work. \n\n\
    For any questions send Spencer Floyd an email at spencer.floyd@gov.bc.ca")

# Checkboxes

lidar_box = Checkbutton(root, text="lidar", variable=lidar_check, bg='#FA6544').place(x=10,y=90)
ortho_box = Checkbutton(root, text="Ortho", variable=ortho_check, bg='#F1A622').place(x=80,y=90)
dem_box = Checkbutton(root, text="DEM", variable=dem_check, bg='#63D849').place(x=150,y=90)
dsm_box = Checkbutton(root, text="DSM", variable=dsm_check, bg='#438BF9').place(x=220,y=90)

# Creates buttons for GUI

copy_btn_1 = Button(root, text="1. Copy Files to Staging_Folder", bg='#003366', fg = "white", command = copy_files).place(x=60,y=125)
check_for_duplicates_btn = Button(root, text="2. Check for Duplicate Files", bg='#003366', fg = "white", command = check_for_duplicates).place(x=70,y=155)
copy_to_lidar_drive_btn = Button(root, text="3. Move to lidar AccessW", bg='#003366', fg = "white", command = copy_to_lidar_drive).place(x=71,y=185)
info_btn = Button(root, text="Instructions", bg='#FCBA19', command = instructions).place(x=110,y=218)
submit_button = Button(root, text="Submit Contract Number", command = submit).place(x=73, y=55)

root.mainloop()