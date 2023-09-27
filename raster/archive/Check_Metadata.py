import pandas as pd
import os
import glob
import csv

# variable for reference header to compare to delivered metadata
ref_headers=['segment_id', 'roll_num', 'frame_num', 'image_file', 'date', 'time', 'flying_height', 'latitude',
             'longitude', 'dec_lat', 'dec_long', 'nts_mapsheet', 'bcgs_mapsheet', 'heading', 'solar_angle',
             'sun_azimuth', 'operation_tag', 'focal_length', 'lens_number', 'nominal_scale', 'gsd', 'emulsion_id',
             'contractor_code', 'req_agency_code', 'aircraft', 'aircraft_reg_num', 'weather', 'remarks', 'stereo_mod',
             'im_frame', 'eop_type', 'eop_x', 'eop_y', 'eop_z', 'omega', 'phi', 'kappa', 'eop_x_stdv', 'eop_y_stdv',
             'eop_z_stdv', 'utm_zone', 'agl', 'cam_s_no', 'calib_date', 'patb_file', 'a1', 'a2', 'a3', 'b1', 'b2',
             'b3', 'c1', 'c2', 'c3']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create list of files from desired directory and open a .csv file to write

# change user defined working directory
os.chdir('D:\Projects\Flood_Plain\metadata')    # !!!!User must enter new directory here!!!
#                                                 !!!!Must be set to location of metadata!!!

# Create a list of files from working directory that have .xlsx extension
flist = list(glob.glob('*.xlsx'))

# Create a csv file and add header information
with open('metadata_errors.csv', 'a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['FILE NAME', 'MISSING HEADER FIELD', 'COLUMNS MISSING DATA'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Start a loop to begin going through metadata file list

for file in flist:

    # create a metadata file from delivered metadata dataframe to be used for checking
    metadata_df = pd.read_excel(file, sheet_name=0, header=0, index_col=False, keep_default_na=True, )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Check to see if any headers are missing

    # create a list of headers in the delivered metadata file
    true_headers = list(metadata_df)

    # Subtract the required reference list header set from the delivered header set
    missing_headers = list(set(ref_headers) - set(true_headers))

    # make sure if no headers are missing, they are displayed as 'none' in .csv file
    if missing_headers == []:
        missing_headers = str('none')
    # convert from list to comma separated string
    else:
        missing_headers = str(missing_headers).strip('[]')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # remove "remarks" header from metadata

    # create array of true/false values if 'remarks' string is present
    # operation is inversed by the '~' bitwise operator
    remarks_array = ~metadata_df.columns.str.contains('remarks')

    # apply true/false array mask to original data frame and index with
    # new header true/false values
    metadata_df_noRem = metadata_df[metadata_df.columns[remarks_array]]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # checking for columns with missing metadata information

    # Drop any columns that contain NaN values
    metadata_no_NaN = metadata_df_noRem.dropna(axis=1, how='any')

    # subtract remaining column headers without NaN values from original column
    # header values so you are only left with columns containing NaN values
    col_missing_data = sorted(list(set(list(metadata_df_noRem)) - (set(list(metadata_no_NaN)))))

    # make sure if no data missing, fields are displayed as 'none' in .csv file
    if col_missing_data == []:
        col_missing_data = 'none'
    # convert from list to comma separated string
    else:
        col_missing_data = str(col_missing_data).strip('[]')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Combine all found missing information and write it to a .csv

    metadata_missing = (file, missing_headers, col_missing_data)

    with open('metadata_errors.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(metadata_missing)