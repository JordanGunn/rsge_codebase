# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , July 2022
# lidar Manipulation program to transform ellipsoidal heights (h) into Orthomteric
# heights(CGVD2013) using NrCANS's latest geoid model  
# info: Lidar@gov.bc.ca

from osgeo import gdal
import laspy
from pyproj import Proj
from pandas import DataFrame
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from tkinter import filedialog as fd
import os
import sys
import vlrs_utm as vlrs_check
import SelectFiles as FL
import disclaimer as dc
import easygui as eg
import webbrowser
import lasattr



#set interpolation algorythm for Geoid grid 
interpol_alg= 'nearest'

def Geoid_DB_check():
    #check if geoid DB file present
    print("OS path:",os.path)
    if (os.path.isfile('GeoidDB.txt')) == True:
        db_file = os.path.isfile('GeoidDB.txt')
        f = open("GeoidDB.txt", "r")
        GeoidList = f.readlines()
        #grab latest Geoidfile from list 
        Geoid_file=GeoidList[-1]

    #create DB file if missing
    elif (os.path.isfile('GeoidDB.txt')) == False:
        f = open("GeoidDB.txt", "w")
        f.write("***** Last file in the list is the active Geoid in use. *****")  
        f.close()
        db_file = os.path.isfile('GeoidDB.txt')
        Geoid_file=""

    return db_file,Geoid_file

def Import_Geoid():
    #Import a geoid file if not existing in the DB file
    image = "geoid.jpg"
    msg = "IMPORT GEOID FILE: Please click on IMPORT and \
    select a suitable NrCAN Geoid file in BYN format."
    choices = ["IMPORT","CANCEL","Search NrCAN"]
    reply = eg.buttonbox(msg, image=image, choices=choices)

    if reply== "IMPORT":
        f = open("GeoidDB.txt", "w")
        #Import Geoid_file into data base file 
        of = fd.askopenfilename(filetypes=[("NrCAN BYN format", "*.byn *.byn")])
        #openfiles=os.path.split(of)# use relative path for geoid file 
        Geoid_file=str(of)
        f.write("====== Last file in the list is the active Geoid in use\n")  
        f.write(Geoid_file)
        f.close()
    
  
        if (os.path.isfile('GeoidDB.txt')) == False:
            sys.exit() 
        return Geoid_file
    
    if reply== "CANCEL":
        sys.exit()
    
    if reply== "Search NrCAN":
     url = 'https://webapp.geod.nrcan.gc.ca/geod/data-donnees/geoid.php?locale=en'
     webbrowser.open(url, new=2)
     sys.exit()




def DegToPixel(point_long_,up_le_long_,res_x_,point_lat_,up_le_lat_,res_y_):
    point_pixel_x_=(point_long_-up_le_long_)/res_x_
    point_pixel_y_=(point_lat_-up_le_lat_)/res_y_
    return point_pixel_x_, point_pixel_y_

def UTM_to_LatLon(las_x,las_y,las_z,zone,zone_id):
    #create Numpy array for coordinate transformation from UTM to Geographic   
    df = DataFrame(np.c_[las_x,las_y], columns=['Meters West', 'Meters North'])
    myProj = Proj("+proj=utm +zone="+str(zone)+" +north +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
    # Convvert UTM to Geographic coordinates
    lon_, lat_ = myProj(df['Meters West'].values, df['Meters North'].values, inverse=True)
    return  lon_,lat_ 


def main(x_OFF,y_OFF,z_OFF,Geoid_file,Input_file,Output_file,ver,ant_ht):

    # ============================= Main program ===================================
    # Read Geoid file & retrieve spatial grid information from the geoidfile 
    ds = gdal.Open(Geoid_file)
    gt=ds.GetGeoTransform()
    proj=ds.GetProjection()
    scale_=ds.GetRasterBand(1).GetScale()
    
    #Import raster dataset as an array with geoid undulation values in the z direction 
    band = ds.GetRasterBand(1) # elevation band 
    array=band.ReadAsArray() *scale_ #apply scale factor to Geoid grid XY int values 
    #Read points in  Lat long and convert into grid system (numpy) 
    num_pixel_x = ds.RasterXSize
    num_pixel_y = ds.RasterYSize

    #retrieve grid reference infos: 
    res_x = gt[1] #resolution longitude
    res_y= gt[5] # resolution latitude
    up_le_long=gt[0]   # upper left grid corner longitue (deg)
    up_le_lat=gt[3]    # upper left grid corner latitude (deg)

    #read lidar points, select lidar pt class and write to output file
    
    las = laspy.read(Input_file)
    print("Input file: ",Input_file)
    print("Geoid     : ",Geoid_file)
    print(f"Point format:       {las.header.point_format}")
    print(f"Number of points:   {las.header.point_count}")
    print(f"Version:   {las.header.major_version}.{las.header.minor_version}")
    print(f"Scale factor:   {las.header.scale}")
    print(f"Min coordinate exents:   {las.header.min}")
    print(f"Max coordinate exents:   {las.header.max}")
    print(f"LiDAR Point classes detected:   {list(dict.fromkeys(list(las.classification)))}")     

    #check for lidar version 1.4
    ver= str(las.header.major_version) +"." + str(las.header.minor_version)
    print ("Version  check =",ver)

    #apply offsets to lidar points if required
    if float(x_OFF) !=0.0:
        las.x=las.x+float(x_OFF)
        print ("Applied X-Offset:",float(x_OFF))

    #apply offsets to lidar points if required
    if float(y_OFF) != 0.0:
        las.y=las.y+float(y_OFF)
        print ("Applied Y-Offset:",float(y_OFF))
    
    #apply offsets to lidar points if required
    if float(z_OFF) !=0.0:
        las.z=las.z+float(z_OFF)
        print ("Applied Z-Offset:",float(z_OFF))

    # apply antenna height offset (reference is ground) if required
    if float(ant_ht) !=0.0:
        las.z=las.z-float(ant_ht)
        print ("Applied Antenna height :",float(ant_ht))

    #apply classification filter if necessarry
    if LiDAR_class > -1:
        las.points = las.points[las.classification == LiDAR_class] # only use specific class

    #transform UTMtoLatLong to pixel(array) coordinates 
    ZONE,ZONE_ID,VERT_FLAG= vlrs_check.check_UTM (Input_file,ver) # read zone from VLRS, check if UTM ZONE exists. -1 -1 if not
    point_long, point_lat = UTM_to_LatLon(las.x,las.y,las.z,ZONE,ZONE_ID)
    point_pixel_x, point_pixel_y = DegToPixel(point_long,up_le_long,res_x,point_lat,up_le_lat,res_y)
    # rearrange lidar points in numpy array
    LiDAR_points = np.array([point_pixel_y,point_pixel_x])
    #derive geoidundulation N from scattered lidar elevations
    N= ndimage.map_coordinates(array, LiDAR_points, order=3, mode=interpol_alg)
    
    #compute average geoid undulation
    av_N=np.average(N)
    min_N=np.min(N)
    max_N=np.max(N)
    print("Min Geoidundulation :",min_N,"m")
    print("Max Geoidundulation :",max_N,"m")
    print("Average Geoidundulation :",av_N,"m")

    #compute Orthometric heights & update las elevations  
    H_Ortho = np.array((las.z -N))
    las.z=H_Ortho

    #write classified data into temporary Las file
    temp_file=str(Output_file)+".las"
    las.write(temp_file)
    
    #update LAS header 
    my_lasattr_obj = lasattr.LasAttr(temp_file)
    my_lasattr_obj.replace_wkt_with_compound_wkt()
    my_lasattr_obj.remove_all_vlrs_evlrs_except_wkt()
    my_lasattr_obj.write_output(Output_file)

    #delete temp file
    os.remove(temp_file)
    
    #Print output metadata on screen
    print("\nOutput file: ",Output_file)
    las_out = laspy.read(Output_file)
    #print(f"Point format:       {las_out.header.point_format}")
    #print(f"Number of points:   {las_out.header.point_count}")
    #print(f"Version:   {las_out.header.major_version}.{las_out.header.minor_version}")
    #print(f"Scale factor:   {las_out.header.scale}")
   # print(f"Min coordinate exents:   {las_out.header.min}")
    #print(f"Max coordinate exents:   {las_out.header.max}")
    print(f"LiDAR Point classes saved:   {list(dict.fromkeys(list(las.classification)))}")
    print (f"Geoid: {Geoid_file}")
    #print ("Applied X_OFFSET_m: ",x_OFF)
    #print ("Applied Y_OFFSET_m: ",y_OFF)
    #print ("Applied Z_OFFSET_m: ",z_OFF)
    #print ("Updating LAS header...\n")
    #print("New Output file created: ",Output_file)
    print("\n========================== Finished  ===============================")

# =========== Check  DB file & Geoid file ====================
DB_file,Geoid_file=Geoid_DB_check()

# Import geoid file if missing
if (os.path.isfile(Geoid_file)) == False:
    msg = "Cannot find a suitable Geoid file.\n\
    Choose CONTINUE to Import a NrCAN Geoid file in BYN format"
    title = "WARNING:"
    if eg.ccbox(msg, title):     # show a Continue/Cancel dialog
        pass  # user chose Continue
        Geoid_file=Import_Geoid()
    else:  # user chose Cancel
        eg.msgbox("******* Exiting Program ********")
        sys.exit(0)

#check Geoid in case user chooses to cancel         
if (os.path.isfile(Geoid_file)) == False: 
    #sys.exit() 
    Geoid_file= Import_Geoid()

#===================================== MAIN =======================================================
#==================================================================================================

# Show disclaimer WINDOW
message, title=dc.get_disclaimer(Geoid_file)
output = eg.msgbox(message, title)

# Processing Parameter WINDOW 
file_list,X_OFF,Y_OFF,Z_OFF,LiDAR_class,Geoid_datum,Ant_hgt =FL.get_filenames(Geoid_file)

# Verbose mode VLRS
verb=0

if file_list:

    #call main  function  
    for fname in list(file_list):
        VERT_CS="NONE"  

        #check if Orthometic height,UTM zone and ID are present in VLR
        ZONE,ZONE_ID,VERT_FLAG= vlrs_check.check_UTM(fname,verb) # read zone and zone_ID from VLRS
         
        if VERT_FLAG=="ORTHOMETRIC":
            print ("Orthometric height detected, cannot apply correction  ")
            #sys.exit()

        elif ZONE==-1 or ZONE_ID ==-1:
            print ("========================================================\n \
            WARNING:Could not find UTM Zone or ZONE ID in VLR record for file: ",fname)
            print ("==================== Exiting Program ====================================\n ")
            #sys.exit()
        else:

            # call main definition
            print ("================== RUNNING MAIN =====================\n ")
            out_f=fname.replace(".las","")
            main(X_OFF,Y_OFF,Z_OFF,Geoid_file,fname,str(out_f)+".orthometric.las",verb,Ant_hgt)
    
else:
    print ("Exiting Program")
    sys.exit()









