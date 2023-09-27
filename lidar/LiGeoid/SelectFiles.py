# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , December 2022
# LAS file and user defined selection of processing parameters using a GUI 
# Data input is a selection of Las files,a NrCan Geoid file name in byn format (e.g. CGG2013.byn) + user defined lidar offsets (Optional)
# Data output: is a LAS file list + a user defined (optional appied) offsets in metric XYZ direction in the Geoidfile DATUM  
# usage at your own risk

import easygui as eg
from osgeo import gdal

def get_filenames(Geoid_file):
    # get HOR&V-Datum of Geoid file
    ds = gdal.Open(Geoid_file)
    gt=ds.GetGeoTransform()
    proj=ds.GetProjection()
    st=str(proj).find("COMPD_CS[\"")
    en_d=proj[(st+10):].find("\"")
    HV_datum=proj[(st+10):(st+10+int(en_d))]
    print("HV_Datum check=",HV_datum)
    
    # open default values in EasyGui window
    msg = "Ellipsoidal to Orthometric height transformation"
    title = "lidar Height Transformation"
    fieldNames = ["X_Offset [m]","Y_Offset [m]","Z_Offset [m]","GEOID","Select point class # (-1=entire data set ):","HOR/V OUTPUT DATUM","PROJECTION","ADD ANTENNA HEIGHT [m]"]
    fieldValues = []  # we start with blanks for the values
    fieldValues= [0.000,0.000,0.0000,Geoid_file,-1,HV_datum,"UTM",0.000]
    fieldValues = eg.multenterbox(msg,title, fieldNames,fieldValues)

    # make sure that none of the fields was left blank
    while 1:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # no problems found
        fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)

    print("Reply was: %s" % str(fieldValues))


    
    openfiles = eg.fileopenbox("Select files", "", filetypes= "*.las", multiple=True)
    return openfiles,fieldValues[0],fieldValues[1],fieldValues[2],int(fieldValues[4]),HV_datum,fieldValues[7]

