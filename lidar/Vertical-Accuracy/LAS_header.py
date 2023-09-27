# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , June 2022
# Args:lidar LAS file
# Output: LAS Header information   

import laspy

def parse_header(filename,par):
    #print("... Extracting LAS header information")
    with laspy.open(filename) as fh:
        xmin=fh.header.x_min
        xmax=fh.header.x_max
        ymin=fh.header.y_min
        ymax=fh.header.y_max
        #zmin=fh.header.z_min
        #zmax=fh.header.z_max
        Las_extends = [xmin,ymin,xmax,ymax]
    # add more fields if needed

    return Las_extends


