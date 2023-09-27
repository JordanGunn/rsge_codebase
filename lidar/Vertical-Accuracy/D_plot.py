
# 2D plot for point clopud visualisation
# Written by Harry Steiner, Harald.Steiner@gov.bc.ca
# Copyright Province oc BC
# 2022-06-20

# Input args : 3D lidar point cloud, GCP points
# Outpuyt graphic plot of GCPs and lidar points

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pyvista as pv
from pyvista import examples


def Two_Dplot(xpoints,ypoints,label,e):
 
    #extract GCP's into single vector 
    x=[]
    y=[]
    z=[]

    for i in range(len(e)):
        #print (e[i]) 
        (X, Y,Z) = e[i] 
        x.append(X)
        y.append(Y)
        z.append(Z)

    plt.title(label)
    plt.plot(xpoints, ypoints, 'o') # lidar
    plt.plot(x, y, 'x') # GCPs

    plt.show()