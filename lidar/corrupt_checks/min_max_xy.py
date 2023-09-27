# ------------------------------------------------------------------------------
# Sometimes, lidar files can have an error where the minimum x dimension
# of the points matches the maximum x dimension, or the minimum y dimension
# matches the maximum y dimension.
#
# This script checks for that error by inspecting the min/max x/y attributes
# in a lidar file header.
#
# To use from other modules, call min_max_xy.check_min_max_x_y()
#
# Written by: Spencer Floyd
# Updated by: Natalie Jackson
# ------------------------------------------------------------------------------

import sys
import os
from tkinter import filedialog
import re

sys.path.append(os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'lasattr'))

import lasattr


def min_max_x_y_find_error(min_x, max_x, min_y, max_y):
    """
    Check if lidar extents have the error of having min and max values
    being equal for either or both of x and y dimensions.

    Args:
        min_x (float): Minimum x extent of lidar file.
        max_x (float): Maximum x extent of lidar file.
        min_y (float): Minimum y extent of lidar file.
        max_y (float): Maximum y extent of lidar file.

    Returns:
        bool:
            - True if there is error
            - False if there is no error
    """
    if min_x == max_x or min_y == max_y:
        error_in_min_max_x_y = True
    else:
        error_in_min_max_x_y = False

    return error_in_min_max_x_y


def generate_text_for_report(min_max_x_y_error_list, lidar_file_count):
    """
    Define text to be printed in the output report.

    Args:
        min_max_x_y_error_list (list of str):
            - List of las/laz file names with errors.
        lidar_file_count (int):
            - Number of lidar files in input directory.

    Returns:
        str:
            - Text to print in output report.
    """
    min_max_error_report_intro = (
        "Min Max X Y Error Report"
        "\n\nLiQCS automatically performs this check on all "
        ".laz/.las files in the input directory."
        f"\n\nLiDAR files checked: {lidar_file_count}"
    )

    if min_max_x_y_error_list:
        error_report_text = (
            f"{min_max_error_report_intro}"
            "\n\nFail. The following .laz/.las files have either:"
            "\n1. The same min x and max x values"
            "\n\ti.e., all points have the same x-value, and fall in a line running north-south"
            "\n2. The same min y and max y values"
            "\n\t(i.e., all points have the same y-value, and fall in a line running east-west)\n\n"
        )
        for i, lidar_file_path in enumerate(min_max_x_y_error_list):
            error_report_text += f"{i + 1}. {lidar_file_path}\n"

    else:
        if lidar_file_count == 1:
            the_each = "the"
        else:
            the_each = "each"
        error_report_text = (
            f"{min_max_error_report_intro}"
            f"\n\nPass. "
            f"The minimum x value of {the_each} lidar file is different from its maximum x value, "
            f"and the minimum y value of {the_each} lidar file is different from its maximum y value."
        )

    return error_report_text


def check_min_max_x_y(input_dir, report_path=None):
    """
    Check all lidar files in an input directory (recursive search)
    for x/y max/min errors.

    If there are lidar files in the input directory,
    write results to a report.

    Args:
        input_dir (str):
            - Full path to input directory containing las/laz files.
        report_path (str) (Optional):
            - Full path to .txt file

    Returns:
        (str):
            - Text with info on what lidar files
                pass/fail the x/y max/min check.
    """
    re_lidar = r'(.laz$|.las$)'
    lidar_file_count = 0
    min_max_x_y_error_list = []

    # Traverse all files in input directory
    for root, subFolder, files in (os.walk(input_dir)):
        for file in files:
            # Identify las/laz files in input directory
            if re.search(re_lidar, file):
                # Count the number of las/laz files in the input directory
                lidar_file_count += 1

                # Get the full path of the lidar file
                lidar_file_path = os.path.join(root, file)

                # Get the las header attributes from the lasattr object.
                attrobj = lasattr.LasAttr(lidar_file_path)

                # Check for errors in the x/y min/max attributes
                lidar_extent_error = min_max_x_y_find_error(
                    attrobj.x_min,
                    attrobj.x_max,
                    attrobj.y_min,
                    attrobj.y_max
                )

                # Add lidar file path to list if it has an error
                if lidar_extent_error:
                    min_max_x_y_error_list.append(lidar_file_path)

    # Only write output if there were lidar files in the input directory
    if lidar_file_count:

        # Generate text for output report
        error_report_text = generate_text_for_report(
            min_max_x_y_error_list,
            lidar_file_count
        )

        if report_path:
            # Write the report text to the report file
            with open(report_path, "a") as min_max_x_y_report:
                min_max_x_y_report.write(
                    error_report_text
                )

    else:
        error_report_text = None

    return error_report_text


def main():
    """
    Run module locally.
    """
    # Define input parameters
    input_dir = filedialog.askdirectory(title="Select input directory containing las/laz files")
    output_dir = filedialog.askdirectory(title="Select output directory for txt report")
    report_path = os.path.join(output_dir, "Min_Max_X_Y_Error_Report.txt")

    # Delete previously versions of the report
    if os.path.exists(report_path):
        os.remove(report_path)

    # Call the primary function of this module
    check_min_max_x_y(input_dir, report_path)


if __name__ == '__main__':
    main()
