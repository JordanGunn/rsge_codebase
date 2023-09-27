# Reference GCP's with LiDAr file list
# Written by Harry Steiner, Harald.Steiner@gov.bc.ca
# Copyright Province oc BC
# 2022-06-06
# Input args : lidar files list, GPS control point list
# Output: lidar file list that contains GCP
# Libraries : Numpy , LAS_header 


import numpy as np
import LAS_header as LH
import laspy
from collections import OrderedDict 

def LAS_GCP_filter (LAS_files,GCP_data_array):
    count=0  
    #New_GCP_list=[]
    GCP_num = len(GCP_data_array)
    LAS_FILE_INDEX =[] # Contains lidar file name
    GCP_INDEX=[]
    GCP_LIST=[]

    for i in list(LAS_files):
        #retrieve LAS min max boundaries
        Las_ext = np.array(LH.parse_header(i,1))
        GCP_INDEX = []
        #GCP_INDEX=[]
        #find GCP coordinates inside LAS point cloud extension

        for j in range(GCP_num):
            
            # compute coordinate differences between LAS file boundaries and check if GCP coordinates inside  
            b= np.array([GCP_data_array[j,0],GCP_data_array[j,1],GCP_data_array[j,0],GCP_data_array[j,1]])
            c= b- Las_ext  

            if c[0] > 0 and c[1] > 0 and c[2]< 0 and c[3] < 0 :
                
                GCP_INDEX.append(GCP_data_array[j])
    
        if GCP_INDEX != []:
            #print ("LAS file",i,"\n GCP found",(GCP_INDEX),"\n ===========----------")  
            LAS_FILE_INDEX.append([i])
            GCP_LIST.append([GCP_INDEX])

    # Number of files found
    num_files = len(GCP_LIST)
    for i in range(len(GCP_LIST)):
        x=np.array(GCP_LIST[i]) # select  GCP array element
        for j in x:
            print("Num entries=",len(j))
            print ("shape=",np.array([j]).shape)
            print (" Count=",count)
            #print ("J 01",j[count])
            for k in range(len(j)):
                print ("J 01",j[k])
            count=count+1
    count = 0
    #print ("LAS file",LAS_FILE_INDEX,"\n GCP found",(GCP_INDEX),"\n ===========----------")  
    return LAS_FILE_INDEX,GCP_LIST,GCP_INDEX,num_files
