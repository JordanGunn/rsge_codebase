# ------------------------------------------------------------------------------
# Written by:
#   Natalie Jackson
# Purpose:
#   This script is used for testing during development
#   of the lasattr.py module.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------------

import os
import sys
import shutil
from datetime import datetime
import subprocess

import lasattr

# ------------------------------------------------------------------------------
# FORMATTING VARIABLES
# ------------------------------------------------------------------------------

dashline = "-" * 80
start_time = datetime.now()
start_time_string = start_time.strftime("%Y%m%d_%H%M")
start_date_string = start_time.strftime("%Y%m%d")


# ------------------------------------------------------------------------------
# INPUT DATA
# ------------------------------------------------------------------------------

test_data_folder = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # path to this script in local cloned repo
    "LASATTR_TEST_DATA"
)
if not os.path.exists(test_data_folder):
    os.mkdir(test_data_folder)

input_data_folder = os.path.join(test_data_folder, "INPUT_DATA")
if not os.path.exists(input_data_folder):
    os.mkdir(input_data_folder)

input_data_dir_contents = os.listdir(input_data_folder)
input_data_options = []

for item in input_data_dir_contents:
    if item.endswith(".las") or item.endswith(".laz"):
        input_data_options.append(item)

num_input_options = len(input_data_options)

if num_input_options > 0:
    file_list_print = ""
    for i, file in enumerate(input_data_options):
        file_list_print += f"\t{i + 1}: {file}\n"
    input_data_choice = 0
    while input_data_choice not in range(1, num_input_options + 1):
        input_data_choice = input(
            f"{dashline}\n"
            f"Input folder:\n\t{input_data_folder}"
            f"\n\nChoose an input file from 1-{str(num_input_options)}, "
            f"or enter Q to quit:"
            f"\n{file_list_print}"
        )
        if input_data_choice.capitalize() == "Q":
            sys.exit()
        try:
            input_data_choice = int(input_data_choice)
        except Exception:
            pass
    input_laslaz_file = input_data_options[input_data_choice - 1]
    input_laslaz_path = os.path.join(input_data_folder, input_laslaz_file)
else:
    # Open the input data folder location in file explorer
    subprocess.Popen(f'explorer "{input_data_folder}"')
    print(
        f"\n{dashline}"
        f"\nPlease put some las and/or laz data in the input data folder, here:"
        f"\n\t{input_data_folder}"
        f"\n\nExiting script, bye!"
        f"\n{dashline}"
    )
    sys.exit()


# ------------------------------------------------------------------------------
# OUTPUT DATA
# ------------------------------------------------------------------------------

output_folder_grandparent = os.path.join(
    test_data_folder,
    "TEST_OUTPUTS",
)
if not os.path.exists(output_folder_grandparent):
    os.mkdir(output_folder_grandparent)

# Clean up output grandparent folder, deleting everything except today's outputs
out_folder_grandparent_contents = os.listdir(output_folder_grandparent)
for item in out_folder_grandparent_contents:
    if item != start_date_string:
        item_path = os.path.join(output_folder_grandparent, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

output_folder_parent = os.path.join(output_folder_grandparent, start_date_string)
if not os.path.exists(output_folder_parent):
    os.mkdir(output_folder_parent)

output_folder = os.path.join(output_folder_parent, start_time_string)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
else:
    print(
        f"{dashline}\nWhoa, another test in the same minute? So fast!"
        "\nHeads up, your log files are going to be re-written. "
        "You'll be okay."
    )

input_las_file_name_and_extension = os.path.splitext(input_laslaz_file)
output_las_file_name = (
    f"{input_las_file_name_and_extension[0]}"  # file name
    f"_EDITED_WITH_LASATTR_{start_time_string}"  # suffix with timestamp
    f"{input_las_file_name_and_extension[1]}"  # file extension
)
output_laslaz_path = os.path.join(output_folder, output_las_file_name)


# ------------------------------------------------------------------------------
# LET'S GO!
# ------------------------------------------------------------------------------

# Don't save logs if you're testing anything with a "proceed" gate
# that relies on interaction with the terminal.
save_logs = False

#if save_logs:
    # Send all print statements to a text file:
    #log_file_name_orig = f"log_{start_time_string}_orig.txt"
    #log_path_orig = os.path.join(output_folder, log_file_name_orig)
    #sys.stdout = open(log_path_orig, 'w')

# Close any open instances of file explorer
# os.system("taskkill /f /im explorer.exe & start explorer")

#print(f"{dashline}\nORIGINAL FILE DETAILS:")
attrobj = lasattr.LasAttr(input_laslaz_path)

#if save_logs:
    #log_write_timer = f"log_{start_time_string}_rewrite_info.txt"
    #write_timer_path = os.path.join(output_folder, log_write_timer)
    #sys.stdout = open(write_timer_path, 'w')
"""
print(
    f"\nAn example of an original attribute:\n\t{attrobj.system_id}"
    f"\nAnother example of an original attribute:\n\t{attrobj.vlr1_value}"
    )
"""

# Examples changing attributes of the LasAttr object:
# attrobj.file_signature = "na"
#attrobj.global_encoding = 654
#attrobj.y_offset = 9999.9999
#attrobj.system_id = "My Cool Company Ltd."
# attrobj.guid4 = (21, 1, 54, 4, 0, 0, 0, 0)
#attrobj.vlr2_record_id = 99
# attrobj.vlr1_value = "Rock em Sock em Robots"
#attrobj.evlr0_record_id = 88
#attrobj.evlr0_value = "Oh hey what's going on I'm an EVLR"
# attrobj.notanattribute = "oh really"
# attrobj.global_encoding = "potatoes"
# attrobj.delete_all_vlrs()
# attrobj.remove_vlr(3)
# attrobj.find_wkt()
#attrobj.replace_wkt_with_compound_wkt()
#attrobj.remove_all_vlrs_evlrs_except_wkt()
# attrobj.remove_evlr(0)
attrobj.log_attr(log_folder=output_folder)

#print(f"{dashline}\n" * 3)
#print(attrobj.vlr1_value)
"""
# Write the new file
attrobj.write_output(output_laslaz_path)

# Open the output folder location in file explorer
subprocess.Popen(f'explorer "{output_folder}"')

if save_logs:
    # Send all print statements to a text file:
    log_file_name_edited = f"log_{start_time_string}_edit.txt"
    log_path_edit = os.path.join(output_folder, log_file_name_edited)
    sys.stdout = open(log_path_edit, 'w')

# Compare outputs by looking at the attributes of the new file:
print(f"{dashline}\nEDITED DATA:")
attrobj_from_updated_file = lasattr.LasAttr(output_laslaz_path)
print(dashline)

if save_logs:
    sys.stdout.close()


# print(attrobj.__dict__)
output_delete_vlrs_dir = os.path.join(output_folder, "DELETE_VLRS")
if not os.path.isdir(output_delete_vlrs_dir):
    os.mkdir(output_delete_vlrs_dir)
output_delete_vlrs = os.path.join(
    output_delete_vlrs_dir,
    output_las_file_name.replace("LASATTR_", "LASATTR_deleteVLRS_")
)
subprocess.Popen(f'explorer "{output_delete_vlrs_dir}"')


if save_logs:
    log_file_name_summary = f"log_{start_time_string}_delete_vlrs.txt"
    log_path_summary = os.path.join(output_folder, log_file_name_summary)
    sys.stdout = open(log_path_summary, 'w')

attrobj_from_updated_file.remove_all_vlrs()
attrobj_from_updated_file.remove_all_evlrs()

attrobj_from_updated_file.write_output(output_delete_vlrs)

no_vrs_attrobj = lasattr.LasAttr(output_delete_vlrs)

if save_logs:
    sys.stdout.close()

if save_logs:
    log_file_name_summary = f"log_{start_time_string}_summary.txt"
    log_path_summary = os.path.join(output_folder, log_file_name_summary)
    sys.stdout = open(log_path_summary, 'w')


for k, key in enumerate(list(attrobj.__dict__)):
    value_in_orig_file = attrobj.__dict__.get(key)
    value_in_new_file = attrobj_from_updated_file.__dict__.get(key)
    if value_in_orig_file != value_in_new_file:
        print(
            f"\nChanged attribute: ({k - 1}) {key}"
            f"\n\n\tOriginal value {type(value_in_orig_file)}:"
            f"\n\t\t{value_in_orig_file}"
            f"\n\n\tNew value {type(value_in_new_file)}:"
            f"\n\t\t{value_in_new_file}"
            f"\n{dashline}"
        )

if save_logs:
    sys.stdout.close()
"""