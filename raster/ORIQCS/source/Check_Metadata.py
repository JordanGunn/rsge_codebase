# ------------------------------------------------------------------------------
# Check_Metadata © GeoBC
# ------------------------------------------------------------------------------
# Excel spreadsheet metadata checking script
# Authors: Sam May and Spencer Floyd
# ------------------------------------------------------------------------------

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
import os
from pathlib import Path
import glob
import csv
import re
import numpy as np
import datetime
from fuzzywuzzy import fuzz

def run_from_gui(flist, outputDir, minSA):
    """
    Run when Metadata is checked in oriqcs. Creates three main outputs:

    1. Metadata_Conditional_Format.xlsx - colours cells red if they don't pass regex and green if they do.

    2. Metadata_Error_Overview.csv - four columns created:
        1.'FILE NAME'
        2.'FILE NAME ERROR'
        3.'MISSING OR INCORRECT HEADER FIELD(S)'
        4.'COLUMNS WITH MISSING OR INCORRECT DATA AND NUMBER OF INCORRECT VALUES'

    3. Column_Errors(folder) - .txt files containing information about column errors 

)

    Args:
        flist (str): list of .xlsx files in input directory
        outputDir (str): path to output directory
        minSA (int): minimum sun angle in DDMMSS taken from user input in oriqcs
    """    


    """
    Create Metadata_Error_Overview.xlsx
    """
    
    # Make a subdirectory in the ORIQCS output directory
    # for metadata test outputs
    outputDir = os.path.join(outputDir, "Metadata")
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)

    # Delete old .xlsx files
    for file_name in glob.glob(outputDir + r'/Metadata_Error_Overview*'):
        os.remove(file_name)

    # Delete temp .xlsx files
    for file_name in glob.glob(outputDir + r'/Metadata_Column_Error_Report*'):
        os.remove(file_name)

    # Delete old folders
    if os.path.isdir(outputDir + r'/Formatted_Metadata'):
        for file_name in glob.glob(outputDir + r'/Formatted_Metadata' + r'/Metadata*'):
            os.remove(file_name)
    
    for file_name in glob.glob(outputDir + r'/Formatted_Metadata*'):
        os.rmdir(file_name)
    
    if os.path.isdir(outputDir + r'/Column_Errors'):
        for file_name in glob.glob(outputDir + r'/Column_Errors' + r'/*.txt'):
            os.remove(file_name)

    for file_name in glob.glob(outputDir + r'/Column_Errors*'):
        os.rmdir(file_name)

    # Create directory for formatted metadata files
    format_folder = outputDir + r'/Formatted_Metadata'


    # Create directory for column error reports
    column_error_folder = outputDir + r'/Column_Errors'

    # Create regular expression list for each metadata field
    regex = [
            # segement_id 0
            '^(\d{1,8})$',
            # roll_num 1
            '^(\d{2}(B|b)(C|c)(D|d)\d{5})$',
            # frame_num 2 
            '^(\d{3}|\d{2}|\d)$',
            # image_file 3
            '^(\d{2}(B|b)(C|c)(D|d)\d{5}_\d{3}_(\d{2}|\d)_(\d{2}|\d)bit_(rgb|rgbir|rgbiR)(.tif|.tiff|.sid|.jpg|.jpeg))$',
            # date 4
            '^(20(\d{2})-[0-1]\d-[0-3]\d)$',
            # time 5
            '^[0-2]\d[0-5]\d[0-5]\d$',
            # flying_height 6
            '^(\d{3,4}|\d{3,4}.\d{1,20})$',
            # latitude 7
            '^([4-6]\d{5}.\d{4})$',
            # longitude 8
            '^(1[1-4]\d{5}.\d{4})$',
            # dec_lat 9
            '(^[4-6]\d.\d{6})',
            # dec_long 10
            '^(-1[1-4]\d.\d{6})',
            # nts_mapsheet (can be null) 11
            '^(|\d{3}[A-P]\d{2})$',
            # bcgs_mapsheet (can be null) 12
            '^(|\d{3}[a-z]\d{3})$',
            # heading 13
            '^([0-3]\d{2}.|\d{2}.|\d.)',
            # solar_angle 14
            '^(\d{6})$',
            # sun_azimuth 15
            '^(\d{6,7})$',
            # operation_tag 16
            '^([A-Z]-\d{3}-([a-zA-Z]{3}|[a-zA-Z]{2}|[a-zA-Z])-\d{2})$',
            # focal_length 17
            '^(\d{2,3}.\d|\d{2,3}.\d|\d{2,3})$',
            # lens_number 18
            '^([A-Za-z0-9]*)$',
            # nominal_scale 19
            '^(|\d:\d*)$',
            # gsd 20
            '^(\d{2})$',
            # emulsion_id 21
            '^3[0-8]$',
            # contractor_code 22
            '^([A-Z]{3})$',
            # req_agency_code 23
            '^([A-Z]{3}|[A-Z]{2}|[A-Z])$',
            # aircraft (can't be null) 24
            '^(.{4,50})$',
            # aircraft_reg_num 25
            '^(.{4,10})$',
            # weather (can be null) 26
            '^(|[^,]+)$',
            # remarks (can be null) 27
            '^(|[^,]+)$',
            # stereo_mod 28
            '^(|\d{1,20})$',
            # im_frame 29
            '^(\d{1,20})$',
            # eop_type 30
            '^(indirect|Indirect|direct|Direct)$',
            # eop_x 31
            '^(\d{6}.\d{3})$',
            # eop_y 32
            '^(\d{7}.\d{3})$',
            # eop_z 33
            '^(\d{1,4}.\d{3})$',
            # omega 34
            '^((|-)\d{1,3}.\d{1,12})$',
            # phi 35
            '^((|-)\d{1,3}.\d{1,12})$',
            # kappa 36
            '^((|-)\d{1,3}.\d{1,12})$',
            # eop_x_stdv 37
            '(\d.\d{3})$',
            # eop_y_stdv 38
            '^(\d.\d{3})$',
            # eop_z_stdv 39
            '^(\d.\d{3})$',
            # utm zone 40
            '(08|09|10|11|12)',
            # agl 41
            '^(\d{3,4}|\d{3,4}.\d{1,20})$',
            # cam_s_no (can't be null) 42
            '^([^,]+$)',
            # calib_date 43
            '^(20(\d{2})-[0-1]\d-[0-3]\d)$',
            # patb_file 44
            '^([A-Za-z0-9_.]*.ori)$',
            # a1 - c3 matrix coefficient values for patb file 45<=
            '^(|-)[0-9].[A-Za-z0-9_*-]*$',
        ]

    # Create a list of field (header) names
    headers = [
            'segment_id',
            'roll_num',
            'frame_num',
            'image_file',
            'date',
            'time',
            'flying_height',
            'latitude',
            'longitude',
            'dec_lat',
            'dec_long',
            'nts_mapsheet',
            'bcgs_mapsheet',
            'heading',
            'solar_angle',
            'sun_azimuth',
            'operation_tag',
            'focal_length',
            'lens_number',
            'nominal_scale',
            'gsd',
            'emulsion_id',
            'contractor_code',
            'req_agency_code',
            'aircraft',
            'aircraft_reg_num',
            'weather',
            'remarks',
            'stereo_mod',
            'im_frame',
            'eop_type',
            'eop_x',
            'eop_y',
            'eop_z',
            'omega',
            'phi',
            'kappa',
            'eop_x_stdv',
            'eop_y_stdv',
            'eop_z_stdv',
            'utm_zone',
            'agl',
            'cam_s_no',
            'calib_date',
            'patb_file',
            'a1',
            'a2',
            'a3',
            'b1',
            'b2',
            'b3',
            'c1',
            'c2',
            'c3'
        ]

    # Create a dictionary of converters for pandas read_excel parameter
    converters = {
                'segment_id': str,
                'roll_num':str,
                'frame_num':str,
                'image_file':str,
                'date': str,
                'time': str,
                'flying_height':str,
                'latitude':str,
                'longitude':str,
                'dec_lat':str,
                'dec_long':str,
                'nts_mapsheet':str,
                'bcgs_mapsheet':str,
                'heading':str,
                'solar_angle':int,
                'sun_azimuth':str,
                'operation_tag':str,
                'focal_length':str,
                'lens_number':str,
                'nominal_scale':str,
                'gsd':str,
                'emulsion_id':str,
                'contractor_code':str,
                'req_agency_code':str,
                'aircraft':str,
                'aircraft_reg_num':str,
                'weather':str,
                'remarks':str,
                'stereo_mod':str,
                'im_frame':str,
                'eop_type':str,
                'eop_x':str,
                'eop_y':str,
                'eop_z':str,
                'omega':str,
                'phi':str,
                'kappa':str,
                'eop_x_stdv':str,
                'eop_y_stdv':str,
                'eop_z_stdv':str,
                'utm_zone':str,
                'agl':str,
                'cam_s_no':str,
                'calib_date':str,
                'patb_file':str,
                'a1':str,
                'a2':str,
                'a3':str,
                'b1':str,
                'b2':str,
                'b3':str,
                'c1':str,
                'c2':str,
                'c3':str}

    error_counter = 0

    # Start a loop to begin going through metadata file list
    for file in flist:
        
        # Get name of file from path
        filename = Path(file).stem

        xlsx = pd.read_excel(file, sheet_name=0, header=0, index_col=None, converters=converters)

        col_count = len(xlsx.columns)

        # create a list of headers in the delivered metadata file
        true_headers = list(xlsx)

        # loop through and compare headers to true headers. If one does not match, add to the missing header variable
        missing_headers = list()
        missing_header_count = 0
        for i, j in zip(headers, true_headers):
            if i != j:
                missing_headers.append(i)
                missing_header_count +=1

        if col_count != 54:
            column_error_report = f'{filename}_Column_Error_Report.txt'
            if not os.path.isdir(column_error_folder):
                os.mkdir(column_error_folder)
            with open(os.path.join(column_error_folder,column_error_report),'a') as column_error:
                column_error.write(f'{col_count} columns instead of 54. Make a copy of .xlsx file to fix and run again.\n\n')
                continue

        # Fuzzy check each header to ensure columns are in the right place
        for x, y in zip(headers, true_headers):
            fuzzy_ratio = fuzz.partial_ratio(x,y)
            if fuzzy_ratio <70:
                error_counter +=1
                if not os.path.isdir(column_error_folder):
                    os.mkdir(column_error_folder)
                column_error_report = f'{filename}_Column_Error_Report.txt'
                with open(os.path.join(column_error_folder,column_error_report),'a') as column_error:
                    column_error.write(f'[{x}] column is named [{y}]. Make a copy of .xlsx file to fix and run again.\n\n')
            else: continue
        if error_counter >0:
            break 

        if not os.path.isdir(format_folder):
                os.mkdir(format_folder)

        df = pd.DataFrame(xlsx)

        df.columns = headers

        # Convert date and time fields to be read appropriately

        df['date'] = pd.to_datetime(df['date']).dt.floor('d')

        df['calib_date'] = pd.to_datetime(df['calib_date']).dt.floor('d')
        
        # Look through each column with corrisponding regex string. If matches regex, replace value with '#'
        df1 = df[headers[0]].astype(str).str.replace(regex[0],'#')
        df1_df = pd.DataFrame(df1)
        df[headers[0]] = df1_df[headers[0]]

        df2 = df[headers[1]].astype(str).str.replace(regex[1],'#')
        df2_df = pd.DataFrame(df2)
        df[headers[1]] = df2_df[headers[1]]

        df3 = df[headers[2]].astype(str).str.replace(regex[2],'#')
        df3_df = pd.DataFrame(df3)
        df[headers[2]] = df3_df[headers[2]]

        df4 = df[headers[3]].astype(str).str.replace(regex[3],'#')
        df4_df = pd.DataFrame(df4)
        df[headers[3]] = df4_df[headers[3]]

        df5 = df[headers[4]].astype(str).str.replace(regex[4],'#')
        df5_df = pd.DataFrame(df5)
        df[headers[4]] = df5_df[headers[4]]

        df6 = df[headers[5]].astype(str).str.replace(regex[5],'#')
        df6_df = pd.DataFrame(df6)
        df[headers[5]] = df6_df[headers[5]]

        df7 = df[headers[6]].astype(str).str.replace(regex[6],'#')
        df7_df = pd.DataFrame(df7)
        df[headers[6]] = df7_df[headers[6]]

        df8 = df[headers[7]].astype(str).str.replace(regex[7],'#')
        df8_df = pd.DataFrame(df8)
        df[headers[7]] = df8_df[headers[7]]

        df9 = df[headers[8]].astype(str).str.replace(regex[8],'#')
        df9_df = pd.DataFrame(df9)
        df[headers[8]] = df9_df[headers[8]]

        df10 = df[headers[9]].astype(str).str.replace(regex[9],'#')
        df10_df = pd.DataFrame(df10)
        df[headers[9]] = df10_df[headers[9]]

        df11 = df[headers[10]].astype(str).str.replace(regex[10],'#')
        df11_df = pd.DataFrame(df11)
        df[headers[10]] = df11_df[headers[10]]

        df12 = df[headers[11]].astype(str).str.replace(regex[11],'#')
        df12_df = pd.DataFrame(df12)
        df[headers[11]] = df12_df[headers[11]]

        df13 = df[headers[12]].astype(str).str.replace(regex[12],'#')
        df13_df = pd.DataFrame(df13)
        df[headers[12]] = df13_df[headers[12]]

        df14 = df[headers[13]].astype(str).str.replace(regex[13],'#')
        df14_df = pd.DataFrame(df14)
        df[headers[13]] = df14_df[headers[13]]

        # Solar Angle is Hashed out because it needs to be formatted later based on minSA variable
        # df15 = df[headers[14]].astype(str).str.replace(regex[14],'#')
        # df15_df = pd.DataFrame(df15)
        # df[headers[14]] = df15_df[headers[14]]

        df16 = df[headers[15]].astype(str).str.replace(regex[15],'#')
        df16_df = pd.DataFrame(df16)
        df[headers[15]] = df16_df[headers[15]]

        df17 = df[headers[16]].astype(str).str.replace(regex[16],'#')
        df17_df = pd.DataFrame(df17)
        df[headers[16]] = df17_df[headers[16]]

        df18 = df[headers[17]].astype(str).str.replace(regex[17],'#')
        df18_df = pd.DataFrame(df18)
        df[headers[17]] = df18_df[headers[17]]

        df19 = df[headers[18]].astype(str).str.replace(regex[18],'#')
        df19_df = pd.DataFrame(df19)
        df[headers[18]] = df19_df[headers[18]]

        df20 = df[headers[19]].astype(str).str.replace(regex[19],'#')
        df20_df = pd.DataFrame(df20)
        df[headers[19]] = df20_df[headers[19]]

        df21 = df[headers[20]].astype(str).str.replace(regex[20],'#')
        df21_df = pd.DataFrame(df21)
        df[headers[20]] = df21_df[headers[20]]

        df22 = df[headers[21]].astype(str).str.replace(regex[21],'#')
        df22_df = pd.DataFrame(df22)
        df[headers[21]] = df22_df[headers[21]]

        df23 = df[headers[22]].astype(str).str.replace(regex[22],'#')
        df23_df = pd.DataFrame(df23)
        df[headers[22]] = df23_df[headers[22]]

        df24 = df[headers[23]].astype(str).str.replace(regex[23],'#')
        df24_df = pd.DataFrame(df24)
        df[headers[23]] = df24_df[headers[23]]

        df25 = df[headers[24]].astype(str).str.replace(regex[24],'#')
        df25_df = pd.DataFrame(df25)
        df[headers[24]] = df25_df[headers[24]]

        df26 = df[headers[25]].astype(str).str.replace(regex[25],'#')
        df26_df = pd.DataFrame(df26)
        df[headers[25]] = df26_df[headers[25]]

        df27 = df[headers[26]].astype(str).str.replace(regex[26],'#')
        df27_df = pd.DataFrame(df27)
        df[headers[26]] = df27_df[headers[26]]

        df28 = df[headers[27]].astype(str).str.replace(regex[27],'#')
        df28_df = pd.DataFrame(df28)
        df[headers[27]] = df28_df[headers[27]]

        df29 = df[headers[28]].astype(str).str.replace(regex[28],'#')
        df29_df = pd.DataFrame(df29)
        df[headers[28]] = df29_df[headers[28]]

        df30 = df[headers[29]].astype(str).str.replace(regex[29],'#')
        df30_df = pd.DataFrame(df30)
        df[headers[29]] = df30_df[headers[29]]

        df31 = df[headers[30]].astype(str).str.replace(regex[30],'#')
        df31_df = pd.DataFrame(df31)
        df[headers[30]] = df31_df[headers[30]]

        df32 = df[headers[31]].astype(str).str.replace(regex[31],'#')
        df32_df = pd.DataFrame(df32)
        df[headers[31]] = df32_df[headers[31]]

        df33 = df[headers[32]].astype(str).str.replace(regex[32],'#')
        df33_df = pd.DataFrame(df33)
        df[headers[32]] = df33_df[headers[32]]

        df34 = df[headers[33]].astype(str).str.replace(regex[33],'#')
        df34_df = pd.DataFrame(df34)
        df[headers[33]] = df34_df[headers[33]]

        df35 = df[headers[34]].astype(str).str.replace(regex[34],'#')
        df35_df = pd.DataFrame(df35)
        df[headers[34]] = df35_df[headers[34]]

        df36 = df[headers[35]].astype(str).str.replace(regex[35],'#')
        df36_df = pd.DataFrame(df36)
        df[headers[35]] = df36_df[headers[35]]

        df37 = df[headers[36]].astype(str).str.replace(regex[36],'#')
        df37_df = pd.DataFrame(df37)
        df[headers[36]] = df37_df[headers[36]]

        df37 = df[headers[36]].astype(str).str.replace(regex[36],'#')
        df37_df = pd.DataFrame(df37)
        df[headers[36]] = df37_df[headers[36]]

        df38 = df[headers[37]].astype(str).str.replace(regex[37],'#')
        df38_df = pd.DataFrame(df38)
        df[headers[37]] = df38_df[headers[37]]

        df39 = df[headers[38]].astype(str).str.replace(regex[38],'#')
        df39_df = pd.DataFrame(df39)
        df[headers[38]] = df39_df[headers[38]]

        df40 = df[headers[39]].astype(str).str.replace(regex[39],'#')
        df40_df = pd.DataFrame(df40)
        df[headers[39]] = df40_df[headers[39]]

        df41 = df[headers[40]].astype(str).str.replace(regex[40],'#')
        df41_df = pd.DataFrame(df41)
        df[headers[40]] = df41_df[headers[40]]

        df42 = df[headers[41]].astype(str).str.replace(regex[41],'#')
        df42_df = pd.DataFrame(df42)
        df[headers[41]] = df42_df[headers[41]]

        df43 = df[headers[42]].astype(str).str.replace(regex[42],'#')
        df43_df = pd.DataFrame(df43)
        df[headers[42]] = df43_df[headers[42]]

        df44 = df[headers[43]].astype(str).str.replace(regex[43],'#')
        df44_df = pd.DataFrame(df44)
        df[headers[43]] = df44_df[headers[43]]

        df45 = df[headers[44]].astype(str).str.replace(regex[44],'#')
        df45_df = pd.DataFrame(df45)
        df[headers[44]] = df45_df[headers[44]]

        df46 = df[headers[45]].astype(str).str.replace(regex[45],'#')
        df46_df = pd.DataFrame(df46)
        df[headers[45]] = df46_df[headers[45]]

        df47 = df[headers[46]].astype(str).str.replace(regex[45],'#')
        df47_df = pd.DataFrame(df47)
        df[headers[46]] = df47_df[headers[46]]

        df48 = df[headers[47]].astype(str).str.replace(regex[45],'#')
        df48_df = pd.DataFrame(df48)
        df[headers[47]] = df48_df[headers[47]]

        df49 = df[headers[48]].astype(str).str.replace(regex[45],'#')
        df49_df = pd.DataFrame(df49)
        df[headers[48]] = df49_df[headers[48]]

        df50 = df[headers[49]].astype(str).str.replace(regex[45],'#')
        df50_df = pd.DataFrame(df50)
        df[headers[49]] = df50_df[headers[49]]

        df51 = df[headers[50]].astype(str).str.replace(regex[45],'#')
        df51_df = pd.DataFrame(df51)
        df[headers[50]] = df51_df[headers[50]]

        df52 = df[headers[51]].astype(str).str.replace(regex[45],'#')
        df52_df = pd.DataFrame(df52)
        df[headers[51]] = df52_df[headers[51]]

        df53 = df[headers[52]].astype(str).str.replace(regex[45],'#')
        df53_df = pd.DataFrame(df53)
        df[headers[52]] = df53_df[headers[52]]

        df53 = df[headers[52]].astype(str).str.replace(regex[45],'#')
        df53_df = pd.DataFrame(df53)
        df[headers[52]] = df53_df[headers[52]]

        df54 = df[headers[53]].astype(str).str.replace(regex[45],'#')
        df54_df = pd.DataFrame(df54)
        df[headers[53]] = df54_df[headers[53]]

        final_df = pd.DataFrame(df)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(outputDir + r'\pandas_conditional.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        final_df.to_excel(writer, sheet_name='Sheet1')

        # Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add a format.
        red_format = workbook.add_format({'bg_color': 'red'})

        # Get the dimensions of the dataframe.
        (max_row, max_col) = final_df.shape

        # Apply a conditional format to the required cell range.
        worksheet.conditional_format(1,1,max_row,max_col,
                                    {'type': 'cell',
                                    'criteria': '!=',
                                    'value': '"#"',
                                    'format': red_format})

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # Read recently saved 'pandas_conditional.xlsx'
        formatted_xlsx = pd.read_excel(outputDir + r'\pandas_conditional.xlsx', sheet_name=0, header=0, index_col=None, converters=converters)

        # Create pandas dataframe from formatted_xlsx
        formatted_df = pd.DataFrame(formatted_xlsx)

        # Read original xlsx file
        xlsx = pd.read_excel(file, sheet_name=0, header=0, index_col=None, converters=converters)
        
        # Create pandas dataframe from original xlsx file
        original_df = pd.DataFrame(xlsx)

        # Write original_df to .xlsx
        original_df.to_excel(outputDir + r'\pandas_original.xlsx')

        xlsx = pd.read_excel(outputDir + r'\pandas_original.xlsx', sheet_name=0, header=0, index_col=None, converters=converters)

        # Create pandas dataframe from xlsx
        original_df = pd.DataFrame(xlsx)

        # Create true false comparison value by comparing original_df and formatted df
        comparison_values = original_df.values == formatted_df

        # Get the Index of all the cells where the value is False, which means the value of the cell differ between the two dataframes
        rows,cols=np.where(comparison_values==False)

        # Iterate over these cells and update the original dataframe value to display the changed value in formatted dataframe
        for item in zip(rows,cols):
            original_df.iloc[item[0], item[1]] = '{}{}'.format(original_df.iloc[item[0], item[1]],formatted_df.iloc[item[0], item[1]])

        # Create a spreadsheet from recently formatted original_df
        original_df.to_excel(outputDir + r'\true_false_diff.xlsx',index=False,header=True)

        # Delete 'Unamed: 0' column which is created through the above processes (not needed)
        del original_df['Unnamed: 0']

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(format_folder + r'\Metadata_Conditional_Format_'+filename+'.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object
        original_df.to_excel(writer, sheet_name='Sheet1')

        # Get the xlsxwriter workbook and worksheet objects
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add formats
        error_format = workbook.add_format({'bg_color': '#fc9272'})

        correct_format = workbook.add_format({'bg_color': '#99d8c9'})

        # Get the dimensions of the dataframe
        (max_row, max_col) = original_df.shape

        #Apply a conditional format to the required cell range.

        # Format minSA based on user input angle in DDMMSS
        worksheet.conditional_format('P2:P10000',
                                    {'type': 'cell',
                                    'criteria': 'less than or equal to',
                                    'value': minSA,
                                    'format': error_format})

        worksheet.conditional_format('P2:P10000',
                                    {'type': 'cell',
                                    'criteria': 'greater than',
                                    'value': minSA,
                                    'format': correct_format})


        # Format all other columns based on '#'
        worksheet.conditional_format('B2:O10000',
                                    {'type': 'text',
                                    'criteria': 'not containing',
                                    'value': '#',
                                    'format': error_format})

        worksheet.conditional_format('B2:O10000',
                                    {'type': 'text',
                                    'criteria': 'containing',
                                    'value': '#',
                                    'format': correct_format})

        worksheet.conditional_format('Q2:BC10000',
                                    {'type': 'text',
                                    'criteria': 'not containing',
                                    'value': '#',
                                    'format': error_format})

        worksheet.conditional_format('Q2:BC10000',
                                    {'type': 'text',
                                    'criteria': 'containing',
                                    'value': '#',
                                    'format': correct_format})


        # Format segment_id header
        worksheet.conditional_format('B1:B1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"segment_id"',
                                    'format': correct_format})

        worksheet.conditional_format('B1:B1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"segment_id"',
                                    'format': error_format})

        # Format roll_num header
        worksheet.conditional_format('C1:C1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"roll_num"',
                                    'format': correct_format})

        worksheet.conditional_format('C1:C1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"roll_num"',
                                    'format': error_format})

        # Format frame_num header
        worksheet.conditional_format('D1:D1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"frame_num"',
                                    'format': correct_format})

        worksheet.conditional_format('D1:D1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"frame_num"',
                                    'format': error_format})

        # Format image_file header
        worksheet.conditional_format('E1:F1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"image_file"',
                                    'format': correct_format})

        worksheet.conditional_format('E1:E1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"image_file"',
                                    'format': error_format})

        # Format date header
        worksheet.conditional_format('F1:F1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"date"',
                                    'format': correct_format})

        worksheet.conditional_format('F1:F1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"date"',
                                    'format': error_format})

        # Format time header
        worksheet.conditional_format('G1:G1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"time"',
                                    'format': correct_format})

        worksheet.conditional_format('G1:G1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"time"',
                                    'format': error_format})
        
        # Format flying_height header
        worksheet.conditional_format('H1:H1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"flying_height"',
                                    'format': correct_format})

        worksheet.conditional_format('H1:H1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"flying_height"',
                                    'format': error_format})

        # Format latitude header
        worksheet.conditional_format('I1:I1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"latitude"',
                                    'format': correct_format})

        worksheet.conditional_format('I1:I1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"latitude"',
                                    'format': error_format})

        # Format longitude header
        worksheet.conditional_format('J1:J1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"longitude"',
                                    'format': correct_format})

        worksheet.conditional_format('J1:J1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"longitude"',
                                    'format': error_format})

        # Format dec_lat header
        worksheet.conditional_format('K1:K1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"dec_lat"',
                                    'format': correct_format})

        worksheet.conditional_format('K1:K1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"dec_lat"',
                                    'format': error_format})

        # Format dec_long header
        worksheet.conditional_format('L1:L1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"dec_long"',
                                    'format': correct_format})

        worksheet.conditional_format('L1:L1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"dec_long"',
                                    'format': error_format})

        # Format nts_mapsheet header
        worksheet.conditional_format('M1:M1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"nts_mapsheet"',
                                    'format': correct_format})

        worksheet.conditional_format('M1:M1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"nts_mapsheet"',
                                    'format': error_format})

        # Format bcgs_mapsheet header
        worksheet.conditional_format('N1:N1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"bcgs_mapsheet"',
                                    'format': correct_format})

        worksheet.conditional_format('N1:N1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"bcgs_mapsheet"',
                                    'format': error_format})

        # Format heading header
        worksheet.conditional_format('O1:O1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"heading"',
                                    'format': correct_format})

        worksheet.conditional_format('O1:O1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"heading"',
                                    'format': error_format})

        # Format solar_angle header
        worksheet.conditional_format('P1:P1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"solar_angle"',
                                    'format': correct_format})

        worksheet.conditional_format('P1:P1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"solar_angle"',
                                    'format': error_format})

        # Format sun_azimuth header
        worksheet.conditional_format('Q1:Q1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"sun_azimuth"',
                                    'format': correct_format})

        worksheet.conditional_format('Q1:Q1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"sun_azimuth"',
                                    'format': error_format})

        # Format operation_tag header
        worksheet.conditional_format('R1:R1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"operation_tag"',
                                    'format': correct_format})

        worksheet.conditional_format('R1:R1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"operation_tag"',
                                    'format': error_format})

        # Format focal_length header
        worksheet.conditional_format('S1:S1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"focal_length"',
                                    'format': correct_format})

        worksheet.conditional_format('S1:S1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"focal_length"',
                                    'format': error_format})

        # Format lens_number header
        worksheet.conditional_format('T1:T1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"lens_number"',
                                    'format': correct_format})

        worksheet.conditional_format('T1:T1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"lens_number"',
                                    'format': error_format})

        # Format nominal_scale header
        worksheet.conditional_format('U1:U1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"nominal_scale"',
                                    'format': correct_format})

        worksheet.conditional_format('U1:U1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"nominal_scale"',
                                    'format': error_format})

        # Format gsd header
        worksheet.conditional_format('V1:V1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"gsd"',
                                    'format': correct_format})

        worksheet.conditional_format('V1:V1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"gsd"',
                                    'format': error_format})

        # Format emulsion_id header
        worksheet.conditional_format('W1:W1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"emulsion_id"',
                                    'format': correct_format})

        worksheet.conditional_format('W1:W1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"emulsion_id"',
                                    'format': error_format})

        # Format contractor_code header
        worksheet.conditional_format('X1:X1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"contractor_code"',
                                    'format': correct_format})

        worksheet.conditional_format('X1:X1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"contractor_code"',
                                    'format': error_format})

        # Format req_agency_code header
        worksheet.conditional_format('Y1:Y1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"req_agency_code"',
                                    'format': correct_format})

        worksheet.conditional_format('Y1:Y1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"req_agency_code"',
                                    'format': error_format})

        # Format aircraft header
        worksheet.conditional_format('Z1:Z1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"aircraft"',
                                    'format': correct_format})

        worksheet.conditional_format('Z1:Z1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"aircraft"',
                                    'format': error_format})

        # Format aircraft_reg_num header
        worksheet.conditional_format('AA1:AA1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"aircraft_reg_num"',
                                    'format': correct_format})

        worksheet.conditional_format('AA1:AA1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"aircraft_reg_num"',
                                    'format': error_format})

        # Format weather header
        worksheet.conditional_format('AB1:AB1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"weather"',
                                    'format': correct_format})

        worksheet.conditional_format('AB1:AB1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"weather"',
                                    'format': error_format})

        # Format remarks header
        worksheet.conditional_format('AC1:AC1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"remarks"',
                                    'format': correct_format})

        worksheet.conditional_format('AC1:AC1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"remarks"',
                                    'format': error_format})

        # Format stereo_mod header
        worksheet.conditional_format('AD1:AD1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"stereo_mod"',
                                    'format': correct_format})

        worksheet.conditional_format('AD1:AD1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"stereo_mod"',
                                    'format': error_format})

        # Format im_frame header
        worksheet.conditional_format('AE1:AE1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"im_frame"',
                                    'format': correct_format})

        worksheet.conditional_format('AE1:AE1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"im_frame"',
                                    'format': error_format})

        # Format eop_type header
        worksheet.conditional_format('AF1:AF1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_type"',
                                    'format': correct_format})

        worksheet.conditional_format('AF1:AF1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_type"',
                                    'format': error_format})

        # Format eop_x header
        worksheet.conditional_format('AG1:AG1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_x"',
                                    'format': correct_format})

        worksheet.conditional_format('AG1:AG1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_x"',
                                    'format': error_format})

        # Format eop_y header
        worksheet.conditional_format('AH1:AH1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_y"',
                                    'format': correct_format})

        worksheet.conditional_format('AH1:AH1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_y"',
                                    'format': error_format})

        # Format eop_z header
        worksheet.conditional_format('AI1:AI1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_z"',
                                    'format': correct_format})

        worksheet.conditional_format('AI1:AI1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_z"',
                                    'format': error_format})

        # Format omega header
        worksheet.conditional_format('AJ1:AJ1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"omega"',
                                    'format': correct_format})

        worksheet.conditional_format('AJ1:AJ1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"omega"',
                                    'format': error_format})

        # Format phi header
        worksheet.conditional_format('AK1:AK1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"phi"',
                                    'format': correct_format})

        worksheet.conditional_format('AK1:AK1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"phi"',
                                    'format': error_format})

        # Format kappa header
        worksheet.conditional_format('AL1:AL1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"kappa"',
                                    'format': correct_format})

        worksheet.conditional_format('AL1:AL1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"kappa"',
                                    'format': error_format})

        # Format eop_x_stdv header
        worksheet.conditional_format('AM1:AM1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_x_stdv"',
                                    'format': correct_format})

        worksheet.conditional_format('AM1:AM1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_x_stdv"',
                                    'format': error_format})

        # Format eop_y_stdv header
        worksheet.conditional_format('AN1:AN1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_y_stdv"',
                                    'format': correct_format})

        worksheet.conditional_format('AN1:AN1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_y_stdv"',
                                    'format': error_format})

        # Format eop_z_stdv header
        worksheet.conditional_format('AO1:AO1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"eop_z_stdv"',
                                    'format': correct_format})

        worksheet.conditional_format('AO1:AO1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"eop_z_stdv"',
                                    'format': error_format})

        # Format utm_zone header
        worksheet.conditional_format('AP1:AP1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"utm_zone"',
                                    'format': correct_format})

        worksheet.conditional_format('AP1:AP1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"utm_zone"',
                                    'format': error_format})

        # Format agl header
        worksheet.conditional_format('AQ1:AQ1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"agl"',
                                    'format': correct_format})

        worksheet.conditional_format('AQ1:AQ1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"agl"',
                                    'format': error_format})

        # Format cam_s_no header
        worksheet.conditional_format('AR1:AR1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"cam_s_no"',
                                    'format': correct_format})

        worksheet.conditional_format('AR1:AR1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"cam_s_no"',
                                    'format': error_format})

        # Format calib_date header
        worksheet.conditional_format('AS1:AS1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"calib_date"',
                                    'format': correct_format})

        worksheet.conditional_format('AS1:AS1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"calib_date"',
                                    'format': error_format})

        # Format patb_file header
        worksheet.conditional_format('AT1:AT1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"patb_file"',
                                    'format': correct_format})

        worksheet.conditional_format('AT1:AT1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"patb_file"',
                                    'format': error_format})

        # Format a1 header
        worksheet.conditional_format('AU1:AU1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"a1"',
                                    'format': correct_format})

        worksheet.conditional_format('AU1:AU1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"a1"',
                                    'format': error_format})

        # Format a2 header
        worksheet.conditional_format('AV1:AV1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"a2"',
                                    'format': correct_format})

        worksheet.conditional_format('AV1:AV1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"a2"',
                                    'format': error_format})

        # Format a3 header
        worksheet.conditional_format('AW1:AW1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"a3"',
                                    'format': correct_format})

        worksheet.conditional_format('AW1:AW1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"a3"',
                                    'format': error_format})
                            
        # Format b1 header
        worksheet.conditional_format('AX1:AX1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"b1"',
                                    'format': correct_format})

        worksheet.conditional_format('AX1:AX1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"b1"',
                                    'format': error_format})

        # Format b2 header
        worksheet.conditional_format('AY1:AY1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"b2"',
                                    'format': correct_format})

        worksheet.conditional_format('AY1:AY1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"b2"',
                                    'format': error_format})

        # Format b3 header
        worksheet.conditional_format('AZ1:AZ1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"b3"',
                                    'format': correct_format})

        worksheet.conditional_format('AZ1:AZ1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"b3"',
                                    'format': error_format})

        # Format c1 header
        worksheet.conditional_format('BA1:BA1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"c1"',
                                    'format': correct_format})

        worksheet.conditional_format('BA1:BA1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"c1"',
                                    'format': error_format})

        # Format c2 header
        worksheet.conditional_format('BB1:BB1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"c2"',
                                    'format': correct_format})

        worksheet.conditional_format('BB1:BB1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"c2"',
                                    'format': error_format})

        # Format c3 header
        worksheet.conditional_format('BC1:BC1',
                                    {'type': 'cell',
                                    'criteria': 'equal to',
                                    'value': '"c3"',
                                    'format': correct_format})

        worksheet.conditional_format('BC1:BC1',
                                    {'type': 'cell',
                                    'criteria': 'not equal to',
                                    'value': '"c3"',
                                    'format': error_format})

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # Delete temp .xlsx files
        for file_name in glob.glob(outputDir + r'/pandas*'):
            os.remove(file_name)
        for file_name in glob.glob(outputDir + r'/true_false*'):
            os.remove(file_name)
        
        """
        Create Metadata_Error_Overview.xlsx
        """

        # Create output path for Metadata_Error_Overview
        overview_output = f'Metadata_Error_Overview.csv'

        # Create a csv file and add header information
        with open(os.path.join(outputDir, overview_output), 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    'FILE NAME',
                    'FILE NAME ERROR',
                    'MISSING OR INCORRECT HEADER FIELD(S)',
                    'COLUMNS WITH MISSING OR INCORRECT DATA AND NUMBER OF INCORRECT VALUES'
                ]
            )

        filenameerror = 0

        # Check the name of the metadata file
        if (re.match(r'^OP\d{2}BMRS\d{3}_\d{4}_AMF_\d{2}bcd\d{5}$', filename)):
            pass
        else: filenameerror += 1

        # Create a metadata file from delivered metadata dataframe to be used for checking
        metadata_df = pd.read_excel(file, sheet_name=0, header=0, index_col=False, converters=converters)
        
        # Create a list of headers in the delivered metadata file
        true_headers = list(metadata_df)

        # Missing_headers = list(set(headers) - set(true_headers))
        missing_headers = list()
        for i, j in zip(headers, true_headers):
            if i != j:
                missing_headers.append(i)

        # Make sure if no headers are missing, they are displayed as 'none' in .csv file
        if not missing_headers:
            missing_headers = str('none')
        # Convert from list to comma separated string
        else:
            missing_headers = str(missing_headers).strip('[]')

        # Check for columns with missing or incorrect metadata information
        col_missing_data = []

        # Loop counters
        y = 0
        num_incorrect = 0

        # Set up loop through each column to check relative regex against each cell
        for y in range(len(metadata_df.columns)):

            if true_headers[y] in headers:
                regexPointer = headers.index(true_headers[y])
                columnPointer = metadata_df.columns.get_loc(true_headers[y])
                for x in range(len(metadata_df)):

                    cell_pointer = metadata_df.iloc[x, columnPointer]

                    # Check 'segement_id' column
                    if regexPointer == 0:
                        if (re.match(regex[0], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'roll_number' column
                    elif regexPointer == 1:
                        if (re.match(regex[1], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'frame_num' column
                    elif regexPointer == 2:
                        if (re.match(regex[2], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'image_file' column
                    elif regexPointer == 3:
                        if (re.match(regex[3], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'date' column
                    elif regexPointer == 4:
                        cell_pointer_convert = datetime.datetime.fromisoformat(cell_pointer)
                        cell_pointer_date = cell_pointer_convert.strftime('%Y-%m-%d')
                        if (re.match(regex[4], str(cell_pointer_date))) is None:
                            num_incorrect += 1

                    # Check 'time' column
                    elif regexPointer == 5:
                            if (re.match(regex[5], str(cell_pointer))) is None:
                                num_incorrect += 1

                    # Check 'flying_height' column
                    elif regexPointer == 6:
                        if (re.match(regex[6], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'latitude' column
                    elif regexPointer == 7:
                        if (re.match(regex[7], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'longitude' column
                    elif regexPointer == 8:
                        if (re.match(regex[8], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'dec_lat' column
                    elif regexPointer == 9:
                        if (re.match(regex[9], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'dec_long' column
                    elif regexPointer == 10:
                        if (re.match(regex[10], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'nts_mapsheet' column
                    elif regexPointer == 11:
                        if (re.match(regex[11], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'bcgs_mapsheet' column
                    elif regexPointer == 12:
                        if (re.match(regex[12], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'heading' column
                    elif regexPointer == 13:
                        if (re.match(regex[13], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'solar_angle' column
                    elif regexPointer == 14:
                        if (re.match(regex[14], str(cell_pointer))):
                            if int(cell_pointer) < minSA:
                                num_incorrect += 1
                        else:  
                            num_incorrect += 1
                            
                    # Check 'sun_azimuth' column
                    elif regexPointer == 15:
                        if (re.match(regex[15], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'operation_tag' column
                    elif regexPointer == 16:
                        if (re.match(regex[16], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'focal_length' column
                    elif regexPointer == 17:
                        if (re.match(regex[17], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'lens_number' column
                    elif regexPointer == 18:
                        if (re.match(regex[18], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'nominal_scale' column
                    elif regexPointer == 19:
                        if (re.match(regex[19], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'gsd' column
                    elif regexPointer == 20:
                        if (re.match(regex[20], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'emulsion_id' column
                    elif regexPointer == 21:
                        if (re.match(regex[21], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'contractor_code' column
                    elif regexPointer == 22:
                        if (re.match(regex[22], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'req_agency_code' column
                    elif regexPointer == 23:
                        if (re.match(regex[23], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'aircraft' column
                    elif regexPointer == 24:
                        if (re.match(regex[24], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'aircraft_reg_num' column
                    elif regexPointer == 25:
                        if (re.match(regex[25], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'weather' column
                    elif regexPointer == 26:
                        if (re.match(regex[26], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'remarks' column
                    elif regexPointer == 27:
                        if (re.match(regex[27], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'stereo_mod' column
                    elif regexPointer == 28:
                        if (re.match(regex[28], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'im_frame' column
                    elif regexPointer == 29:
                        if (re.match(regex[29], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'eop_type' column
                    elif regexPointer == 30:
                        if (re.match(regex[30], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'eop_x' column
                    elif regexPointer == 31:
                        if (re.match(regex[31], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'eop_y' column
                    elif regexPointer == 32:
                        if (re.match(regex[32], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'eop_z' column
                    elif regexPointer == 33:
                        if (re.match(regex[33], str(cell_pointer))) is None:
                            num_incorrect += 1
                    
                    # Check 'omega' column
                    elif regexPointer == 34:
                        if (re.match(regex[34], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'phi' column
                    elif regexPointer == 35:
                        if (re.match(regex[35], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'kappa' column
                    elif regexPointer == 36:
                        if (re.match(regex[36], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'eop_x_stdv' column
                    elif regexPointer == 37:
                        if (re.match(regex[37], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'eop_y_stdv' column
                    elif regexPointer == 38:
                        if (re.match(regex[38], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'eop_z_stdv' column
                    elif regexPointer == 39:
                        if (re.match(regex[39], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'utm_zone' column
                    elif regexPointer == 40:
                        if (re.match(regex[40], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'agl' column
                    elif regexPointer == 41:
                        if (re.match(regex[41], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'cam_s_no' column
                    elif regexPointer == 42:
                        if (re.match(regex[42], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'calib_date' column
                    elif regexPointer == 43:
                        cell_pointer_convert = datetime.datetime.fromisoformat(cell_pointer)
                        cell_pointer_date = cell_pointer_convert.strftime('%Y-%m-%d')
                        if (re.match(regex[43], str(cell_pointer_date))) is None:
                            num_incorrect += 1

                    # Check 'patb_file' column
                    elif regexPointer == 44:
                        if (re.match(regex[44], str(cell_pointer))) is None:
                            num_incorrect += 1

                    # Check 'a1-c3' columns
                    elif regexPointer >= 45:
                        if (re.match(regex[45], str(cell_pointer))) is None:
                            num_incorrect += 1


                if num_incorrect >= 1:
                    incorrect_str = true_headers[y] + ": " + str(num_incorrect)
                    col_missing_data.append(incorrect_str)
                x = 0
                num_incorrect = 0
                cell_pointer = ''
                incorrect_str = ''

        # Make sure if no data missing, fields are displayed as 'none' in .csv file
        if col_missing_data == []:
            col_missing_data = 'none'

        # Convert from list to comma separated string
        else:
            col_missing_data = str(col_missing_data).strip('[]')

        if filenameerror == []:
            filenameerror = 'File named properly'
        
        else: filenameerror = 'File is NOT named properly'


        # Combine all found missing information and write it to a .csv
        metadata_missing = (file, filenameerror, missing_headers, col_missing_data)

        # Write metadata_missing to 'Metadata_Error_Overview.csv'
        with open(os.path.join(outputDir, overview_output), 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(metadata_missing)
            writer.writerow('')


def main():
    inputDir = r'C:\__Metadata'
    outdir = r'C:\__Metadata\Output'
    flist = (glob.glob(inputDir + "/" + '*.xlsx'))

    run_from_gui(flist, outdir,430000)


if __name__ == '__main__':
    main()