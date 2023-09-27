    
# Import libraries
#from mpl_toolkits import mplot3d
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D
import laspy
#import numpy.ma as ma
#from numpy.random import uniform, seed

def ThreeD_plot(X,Y,Z,GCP,INTERP):
#extract data into single vector  
    x=[]
    y=[]
    z=[]
    #extract single 1D coordinate arrays 
    for i in range(len(GCP)):
        #print (e[i]) 
        XX,YY,ZZ = GCP[i]
        x.append(XX)
        y.append(YY)
        z.append(ZZ)
 

    # define grid.
    xi = np.linspace(min(X),max(X),100)
    yi = np.linspace(min(Y),max(Y),100)
  

    # grid the data.
    #zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='linear')    
    zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method=INTERP)  

    
    #contour the gridded data, plotting dots at the randomly spaced data points.
    CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
    CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
    plt.colorbar() # draw colorbar

    # plot data points.
    plt.scatter(x,y,marker='o',c='b',s=7)
    plt.scatter(X,Y,marker='x',c='r',s=3)
    plt.xlim(min(X),max(X))
    plt.ylim(min(Y),max(Y))
    plt.title(INTERP)
    plt.show()

    return

