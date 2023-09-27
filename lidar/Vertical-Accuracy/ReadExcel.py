# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , June 2022
# Read content of a spreadsheet in  .xlxs format and return data in numpy array 

import pandas as pd 
import xlrd

def read_excel(GCP_file,COLMNS,PT):
    #Extract  GCP coordinates from file and write into numpy array
    #COLMNS = Number of data columns to read from 
    array=pd.DataFrame(pd.read_excel(GCP_file,sheet_name=0,usecols=COLMNS)).to_numpy()
    PT_ID=pd.DataFrame(pd.read_excel(GCP_file,sheet_name=0,usecols=PT)).to_numpy()
    num_pts = len(array)
    return array,num_pts,PT_ID
