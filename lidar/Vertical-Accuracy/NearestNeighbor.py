# Nearest neighbor search between Groubd control pt and LiDAr point cloud
# Written by Harry Steiner, Harald.Steiner@gov.bc.ca
# Copyright Province oc BC
# 2022-06

# Input args : lidar point cloud file, GPS control points,K- closest number of points, nearest neighbor leaf
# Output: closest LidAr point clous index of K-points
# Method: Verical plumbline check between a control point and a lidar derived surface


from re import A
import numpy as np
from sklearn.neighbors import KDTree
import laspy

def nearest_KD (GCP_data_array,LAS_file,K,leaf_s,GCP_LIST):

    with laspy.open(LAS_file) as fh:
        las = fh.read()
        # transpose Las array if importe from numpy 
        Lidar_pts=np.array([las.x,las.y,las.z]).T

    # concatenate GCP and lidar point into one large array
    X =  np.concatenate((GCP_LIST, Lidar_pts))
    
    # compute KD-tree 
    tree = KDTree(X, leaf_size=leaf_s)              

   
    # Compute nearest neighbor (lidar and GCP in on array)
        # nearest neighbor : the number of the nearest neighbors 
        #                    is increased by adding GCP's (k=K+1+len(GCP_LIST)) 
    dist, nn_pt_index = tree.query(X, k=K+1+len(GCP_LIST))  
    
    # reduce array(S) to COLUMN=Number of GCP's(rather to full Lidar pt numbers)
    dist=np.array(dist) 
    nn_pt_index =  np.array(nn_pt_index)         
    
    # remove nearest neighbors relations between GCP (in case they are closeby)
 
    KD_pt_index= np.concatenate((np.vstack(nn_pt_index[0:(len(GCP_LIST)),0]),nn_pt_index[0:(len(GCP_LIST)),len(GCP_LIST):]), axis=1)
    KD_pt_dist= np.concatenate((np.vstack(dist[0:(len(GCP_LIST)),0]),dist[0:(len(GCP_LIST)),len(GCP_LIST):]), axis=1)
    #print("KD_pt_index=\n",KD_pt_index)
    #print("KD_pt_dist=\n",KD_pt_dist)
    NN_las_x=[]
    NN_las_y=[]
    NN_las_z=[]
    
    for i in range(len(KD_pt_index)):
        a=np.array(KD_pt_index[i])
        for x in a:
            #print ("Pt index=",int(x), "  Las x=",las.x[int(x)])
            NN_las_x.append(las.x[int(x)])
            NN_las_y.append(las.y[int(x)])
            NN_las_z.append(las.z[int(x)])
            

    NN_las_x = np.array(NN_las_x)
    NN_las_y = np.array(NN_las_y)
    NN_las_z = np.array(NN_las_z)
 
    return KD_pt_index,KD_pt_dist,NN_las_x,NN_las_y,NN_las_z