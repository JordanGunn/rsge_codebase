import re
import csv
import datetime
import os
import pandas as pd

class LidarSummary:

    """

    This class generates a tabular lidar dataset summary from a directory of lasinfo text files.

    information summarized is as follows:

    > Filename
    > Global Encoding
    > Point Data Format
    > Las major and minor version
    > Coordinate reference system metadata (wkt format)
    > GPS time (min/max)
    > Local date/time (converted from GPS time)
    > flightline (start/end)
    > X min/max
    > Y min/max
    > Bounding Box (in WKT polygon format)
    > Classes
    > Flags

    Written by: Brett Edwards
    """

    # Requirements for the lidar file to pass tests and be a 'good' file
    global_encoding_req = '17'
    version_req = '1.4'
    pt_format_req = '6'
    cmpd_proj_req = 'yes'
    gpstime_req = 604800 #gps time must be greater than this value, which is the maximum gps week time
    classes = ['1;2;7']


    def __init__(self, text_file):
        self.good_file = True   # Default status is that the lidar file is a good dog (meets requirements)

        with open(text_file, 'r', errors='ignore') as f:
            self.info = f.read()    # Open the lasinfo file

        self.file = re.split(R"\.|\\", text_file)[-2] # Store the las/laz filename

        self.info_dict = {} # Create a dictionary to store all of the lasinfo that's being searched for in this class

        self.read_info()    # Run the read_info method, storing all of the info parameters on instantiation of the class in the info_dict 


    def read_info(self):
        self.filename() # run the filename method, etc....
        self.global_encoding()
        self.version()
        self.point_format()
        self.projection()
        gps_time = self.gps_time()
        self.datetime(gps_time)
        self.classes()
        self.flightlines()
        self.flags()
        self.vlrs()
        self.total_points()
        self.xy_minmax()
        self.bbox()
        self.check_file()

    
    def check_file(self): # Check if file is a good dog or bad dog based on class variable requirements
        if self.info_dict['Global_Encoding'] != LidarSummary.global_encoding_req or \
            self.info_dict['Version'] != LidarSummary.version_req or \
            self.info_dict['Point_Data_Format'] != LidarSummary.pt_format_req or \
            self.info_dict['Compound_Projection'] != LidarSummary.cmpd_proj_req or \
            float(self.info_dict['GPS_Start']) <= LidarSummary.gpstime_req:
            
            # TODO classes requirement
            
            self.good_file = False
    

            

    def filename(self): # add filename to dictionary and return it, just in case we want to use it later
        fname = re.search(R"report for '(.*.la[s|z])'", self.info)
        if fname:
            basename = re.split(R'\\', fname[1])
            self.info_dict['Filename'] = basename[-1]
            return(fname[1])
        else:
            self.info_dict['File'] = self.file
            return self.file


    def global_encoding(self): # add global encoding to dictionary
        glob_enco = re.search(R'(global_encoding:)\s+(\d+)', self.info) # regex to locate global encoding value in text file
        
        if glob_enco:
            self.info_dict['Global_Encoding'] = glob_enco[2]
            return glob_enco[2]

    def flightlines(self): # add flight line #s (point source ids) to dict
        fl_nums = re.search(R'point_source_ID\s+(\d+)\s+(\d+)', self.info)

        if fl_nums:
            self.info_dict['Flightline_Start'] = fl_nums[1]
            self.info_dict['Flightline_End'] = fl_nums[2]
            return fl_nums[1], fl_nums[2]


    def version(self): # add version to dictionary 
        version = re.search(R'(major.minor:)\s+(\d\.\d)', self.info) #regex

        if version:
            self.info_dict['Version'] = version[2]
            return version[2]
    

    def point_format(self): # add point data format to dict
        pt_frmt = re.search(R'(point data format:)\s+(\d+)', self.info) # regex

        if pt_frmt:
            self.info_dict['Point_Data_Format'] = pt_frmt[2]
            return pt_frmt[2]


    def projection(self): # add projection info to dict
        wkt_compound = re.search(R'(COMPD_CS\[\")([^\"]*)', self.info) # regex to search for compound projection
        if wkt_compound:
            self.info_dict['Projection'] = wkt_compound[2]
            self.info_dict['Compound_Projection'] = 'yes'
            return wkt_compound[2]
        
        wkt_proj = re.search(R'(PROJCS\[\")([^\"]*)', self.info) # if compound not found, we'll look for the horizontal wkt projection
        if wkt_proj:
            self.info_dict['Projection'] = wkt_proj[2]
            self.info_dict['Compound_Projection'] = 'no'
            return wkt_proj[2]

        self.info_dict['Projection'] = 'wkt missing' # if the wkt projection isn't found, say so
        self.info_dict['Compound_Projection'] = 'no'


    def gps_time(self): # locate start and end gps times and add to dict
        gps = re.search(R'gps_time\s([-]?\d+\.\d+)\s(\d+\.\d+)', self.info) # regex
        if gps:
            self.info_dict['GPS_Start'] = gps[1]
            self.info_dict['GPS_End'] = gps[2]
            return float(gps[1]), float(gps[2])
        else:
            self.info_dict['GPS_Start'] = 0
            self.info_dict['GPS_End'] = 0
    

    def datetime(self, adjusted_gps_time): # convert gps times to readable date and time if possible. If not possible, tell us why
        
        
        try:
            gps_start, gps_end = adjusted_gps_time
            if gps_start > 604800: # convert gps time if it is greater than the maximum gps week time (meaning it is adjusted standard time)
                self.info_dict['Date_Time_Start'] = convert_gps_time(gps_start)
            elif gps_start > 0:
                self.info_dict['Date_Time_Start'] = 'GPS Week time'
            else:
                self.info_dict['Date_Time_Start'] = 'No GPS time'

            if gps_end > 604800:
                self.info_dict['Date_Time_End'] = convert_gps_time(gps_end)
            elif gps_end > 0:
                self.info_dict['Date_Time_End'] = 'GPS Week time'
            else:
                self.info_dict['Date_Time_End'] = 'No GPS time'

        except:
            self.info_dict['Date_Time_Start'] = 'Error converting GPS time'
            self.info_dict['Date_Time_End'] = 'Error converting GPS time'


    def classes(self): # Find the classes 
        class_list = []
        class_rgx = re.findall(R"\d+\s+.*\s\((\d+)\)[^']", self.info) # regex

        for clas in class_rgx:
            class_list.append(clas)

        classes = ';'.join(class_list)
        self.info_dict['Classes'] = classes
        return classes
        
    
    def xy_minmax(self): # find x y min max of lidar file
        min_xy = re.search(R'min x y z:\s+(\d+\.\d+)\s+(\d+\.\d+)', self.info) # regex
        if min_xy:
            self.info_dict['x_min'] = min_xy[1]
            self.info_dict['y_min'] = min_xy[2]

        max_xy = re.search(R'max x y z:\s+(\d+\.\d+)\s+(\d+\.\d+)', self.info) # regex
        if max_xy:
            self.info_dict['x_max'] = max_xy[1]
            self.info_dict['y_max'] = max_xy[2]
        
        return min_xy[1], min_xy[2], max_xy[1], max_xy[2]


    def flags(self): # find if any points have flags (overlap, synthetic, etc) and how many points have those flags
        flag_list = []

        flag_rgx = re.findall(R'flagged as\s(.*:.*)', self.info)
        for flag in flag_rgx:
            flag_list.append(flag)

        flags = ';'.join(flag_list)

        self.info_dict['Flags'] = flags
        return flags


    def vlrs(self): # Find how many VLRs there are in the file
        vlrs = re.search(R'number var. length records: (\d+)', self.info)
        
        if vlrs is not None:
            self.info_dict['#VLRs'] = vlrs[1]
            return vlrs[1]


    def total_points(self): # Find how many total points there are (it's stored in a different location in the header for las 1.2 vs 1.4)
        if self.info_dict['Version'] == '1.4':
            total_pts = re.search(R'extended number of point records:\s(\d+)', self.info)
            self.info_dict['Total_Points'] = total_pts[1]
            return total_pts[1]
        elif self.info_dict['Version'] == '1.2':
            total_pts = re.search(R'number of point records:\s+(\d+)', self.info)
            self.info_dict['Total_Points'] = total_pts[1]
            return total_pts[1]

    
    def bbox(self): # create a WKT bounding box for the lidar file
        xmin, xmax, ymin, ymax = self.info_dict['x_min'], self.info_dict['x_max'], self.info_dict['y_min'], self.info_dict['y_max']
        bbox_poly = f"POLYGON (({xmin} {ymax}, {xmax} {ymax}, {xmax} {ymin}, {xmin} {ymin}, {xmin} {ymax}))"

        self.info_dict['wkt_bbox'] = bbox_poly
        return bbox_poly


    def output(self, output_path, write_errors=False):  # write the summary results out to csv files. By default, write the 'errors' csv
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        output_csv = f'{output_path}\\lidar_summary_{date}.csv'
        error_csv = f'{output_path}\\lidar_summary_errors_{date}.csv'

        if not os.path.exists(output_csv): # if the file doesn't exist, create it and write the header 
            with open(output_csv, 'a', newline='') as csvfile:
                fieldnames = self.info_dict.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader() # write the header

        with open(output_csv, 'a', newline='') as csvfile:
            fieldnames = self.info_dict.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(self.info_dict) # write the entry into the summary file

        if write_errors:    # if write_errors=True, write out the errors csv
            if self.good_file == False: # if the file formatting is bad, write it to the "error" csv
                if not os.path.exists(error_csv):
                    with open(error_csv, 'a', newline='') as csvfile:
                        fieldnames = self.info_dict.keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()

                with open(error_csv, 'a', newline='') as csvfile:
                    fieldnames = self.info_dict.keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(self.info_dict)

        return output_csv

def find_format_errors(lidar_summary, output_path, save_output=True):
    """
    Input is a lidar summary csv file from the LidarSummary class output and an output path. Result is a csv showing all files with errors and a text file summarizing those errors
    into their specific causes.
    """
    date = datetime.datetime.today().strftime('%Y-%m-%d') # set date to today for later use

    df = pd.read_csv(lidar_summary) # read the input summary csv into a dataframe  

    version = df['Version'] != 1.4      # find files where the version is not 1.4
    ver_issues = version.sum()          # count how many aren't version 1.4

    global_encoding = df['Global_Encoding'] != 17   # find files where the verison is not 17
    ge_issues = global_encoding.sum()

    projection = df['Compound_Projection'] == 'no'  # find files that don't have a compound projection
    prj_issues = projection.sum()

    # classes = ~df['Classes'].isin(['1;2;7', '1;2'])   # TODO possibly implement a check on classes
    # class_issues = classes.sum()

    gps = df['GPS_Start'].astype(float) <= 604800   # find files that are not adjusted standard GPS time
    gps_issues = gps.sum()

    flightline = df['Flightline_Start'] == 0    # Find files without flight line numbers 
    fl_issues = flightline.sum()

    flags = ~df['Flags'].isnull()   # Find files with points flagged as anything
    flag_issues = flags.sum()

    date_filter = df['GPS_Start'] > 604800          # create filter to find the files that likely have adjusted standard GPS time
    year_list = df[date_filter].Date_Time_Start.str[:4].tolist()        # Pull the first 4 digits from these filtered dates (the first 4 digits being the year)
    years = set(year_list)      # Turn these years into a set to remove duplicates

    df_errors = df[version | global_encoding | projection | gps | flightline | flags]       # Put all of these files where issues were found together into a single dataframe. '|' is 'or' in pandas

    with open(f'{output_path}\\format_error_summary_{date}.txt', mode='w') as out:          # Print a summary of the errors found to a text file
        print(f"{ver_issues} out of {len(df.index)} with version issues", file=out)
        print(f"{ge_issues} out of {len(df.index)} with global encoding issues", file=out)
        print(f"{prj_issues} out of {len(df.index)} with projection issues", file=out)
        # print(f"{class_issues} out of {len(df.index)} with class issues", file=out)
        print(f"{gps_issues} out of {len(df.index)} with GPS time issues", file=out)
        print(f"{fl_issues} out of {len(df.index)} with flightline issues", file=out)
        print(f"{flag_issues} out of {len(df.index)} with points flagged", file=out)
        print(f"\nYears from GPS times: {years}", file=out)
        print(f"\n\nTotal number of files with issues: {len(df_errors.index)}", file=out)
    
    if save_output:          # If save_output=True, write the summary of all files with errors to a csv
        df_errors.to_csv(os.path.join(output_path, f'lidar_summary_errors_{date}.csv'), index=False)

    return df_errors


def countleaps(gpsTime):
    """Count number of leap seconds that have passed."""

    # a tuple of the gps times where leap seconds were added
    leaps = (
        46828800, 78364801, 109900802, 173059203, 252028804,
        315187205, 346723206, 393984007, 425520008, 457056009,
        504489610, 551750411, 599184012, 820108813, 914803214,
        1025136015
    )

    nleaps = 0
    for leap in leaps:
        if gpsTime >= leap:
            nleaps += 1

    return nleaps


def convert_gps_time(time_value):

    # number of seconds between the start of unix time (Jan 1, 1970) and gps time (Jan 6, 1980)
    offset = 315964800

    time = float(time_value)
    time += 1e9 #unadjusted gps time
    unixtime = time + offset - countleaps(time)
    datetimestr = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return datetimestr


# if __name__ == '__main__':
#     df = pd.read_csv(R"D:\__code__\vscode\lasinfo\lidar_summary.csv")
        
#     df['Start Time (PDT)'] = df['GPS Start'].map(convert_gps_time)
#     df['End Time (PDT)'] = df['GPS End'].map(convert_gps_time)

#     print(df.to_string())

#     # df.to_csv('out.csv', index=False)



if __name__=='__main__':
    import glob
    from tkinter import filedialog, Tk
    Tk().withdraw()

    # prompt for indir and outdir
    indir = filedialog.askdirectory(title="Select input lasinfo directory")
    outdir = filedialog.askdirectory(title="Select output directory")

    files = glob.glob(os.path.join(indir, '*.txt'))


    for f in files:
        try:
            test = LidarSummary(f)
            summary_csv = test.output(outdir, write_errors=False) # the output method writes all files to a csv, and returns the path for the output
        except:
            with open(os.path.join(outdir, 'problem_files.txt'),'a') as probs:
                print(f, file=probs)

    find_format_errors(summary_csv, outdir)     # Run the find_format_errors function on the result of the LidarSummary output

    print('Done!')

 
