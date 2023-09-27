# ------------------------------------------------------------------------------
# Script to demonstrate:
#   1. replacing a horizontal-only WKT with a compound WKT (default CGVD2013)
#   2. removing all non-WKT VLRs
# in a las/laz file using lasattr.py
# ------------------------------------------------------------------------------

import lasattr

input_file_path = r"C:\Python_DEVELOPER\LiGeoidApp\Las_file\LSmall cobble-hill_Ellipsoidal_v1.4.las"
output_file_path =  r"C:\Python_DEVELOPER\LiGeoidApp\Las_file\LSmall cobble-hill_Ellipsoidal_to_CGVD2013.las"


my_lasattr_obj = lasattr.LasAttr(input_file_path)

my_lasattr_obj.replace_wkt_with_compound_wkt()

my_lasattr_obj.remove_all_vlrs_evlrs_except_wkt()

my_lasattr_obj.write_output(output_file_path)

# Make a new LasAttr object to print the new attributes to the terminal (optional)
new_lasattr_obj = lasattr.LasAttr(output_file_path)
