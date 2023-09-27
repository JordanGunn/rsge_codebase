# Vertical accuracy checking for lidar derived surface
# Written by Harry Steiner, Harald.Steiner@gov.bc.ca
# Copyright Province oc BC
# 2022-05-30

# Input args : lidar point cloud, GPS control points
# Output: Statement of achieved vertical lidar accuracy
# Method: Verical plumbline check between a control point and a lidar derived surface
# 

# ========= Libraries ================
#from cProfile import label
#from turtle import xcor
import easygui as eg
import SelectFiles as FL
import ReadExcel as EX
import LasFilter as LF
import NearestNeighbor as NKD
import D_plot as TP
import PtToSurface as VDIF
import ThreeDplot as T3Plot
import GridSurface as S3DPlot
import TIN as T
import numpy as np
import lasattr 
import os



# ================== STEPS INVOLVED===================================================
# 1) Select GCP and LAS file(s) using easyGUI , create file list, create GCP array (numpy)
# 2) Create lidar file list contaiing GCP's,  find nearest neighbor LIDAR points for each GCP in LAS file
# 4) Generate surface from lidar point cloud with the control point in the center
# 5) Assess planarity of the surface usign lidar points
# 6) Generate plumline check 
# 7) Write output report 
# ====================================================================================


# 1) Select GCP and LAS file(s) using easyGUI , create file list, create GCP array (numpy)
COL='B:D' # Coordinate cells
PT='A'# ID cells

GCP_file=FL.get_filenames("","*.xlsx","SELECT GROUND CONTROL","GCP control file",True) # GCP file
GCP_data_array,GCP_num,PT_ID= EX.read_excel(GCP_file[0],COL,PT)
print ("Importing ",GCP_num," GCP points\n",PT_ID)

LAS_files=FL.get_filenames("","*.LAS","SELECT lidar FILES","lidar file",False) # lidar file
print ("Importing ",len(LAS_files)," LAS_file(s)")
print (np.array(LAS_files).T,"\n\n =============================== Computing KD tree and Nearest Neighbor =========================================")


# 2) Create lidar file list containing GCP's and coordinates,  find nearest neighbor LIDAR points for each GCP in LAS file
k=20 # Number of closest points for nearest neighbor 
leaf_s=30 # Leaf size

# File list containg GCP data
LAS_FILE_INDEX,GCP_LIST,GCP_INDEX,num_files= LF.LAS_GCP_filter (LAS_files,GCP_data_array) # File list containg GCP data

print ("INPUT PARAMETER(s):\n Nearest Neighbors =",k)
print ("Leaf size =",leaf_s)

for i in range(len(LAS_FILE_INDEX)):    
    
    print ("\n*** FILE: ",LAS_FILE_INDEX[i])
    x=np.array(GCP_LIST[i]) # convert GCP list into np array
    GCP=np.vstack(x) # convert ground control coordinates from excel 
                     # and extract into coordniate pairs as a vertical array   
    print ("\nGCP Number: ",len(GCP))
    print (GCP)

    # Compute KD-TRee and Nearest Neighbor search for each ground control and file 
    point_index,KD_pt_dist,NN_las_x,NN_las_y,NN_las_z = NKD.nearest_KD (GCP_data_array,str(*LAS_FILE_INDEX[i]),k,leaf_s,GCP)
    V_diff= VDIF.VDIFF(NN_las_x,NN_las_y,NN_las_z,GCP,'cubic')
    print ("Vdiff= ",V_diff)
    
    print ("================================= END: KD-TRee and N-Neighbor ====================================")   

# Interpolate GCP elevation from surface
   
   
    #TP.Two_Dplot(NN_las_x,NN_las_y,"GCP/lidar nearest neighbors",GCP)
    T3Plot.ThreeD_plot(NN_las_x,NN_las_y,NN_las_z,GCP,'nearest')
    T3Plot.ThreeD_plot(NN_las_x,NN_las_y,NN_las_z,GCP,'linear')
    T3Plot.ThreeD_plot(NN_las_x,NN_las_y,NN_las_z,GCP,'cubic')