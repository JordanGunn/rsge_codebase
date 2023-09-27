# Import libraries
#from mpl_toolkits import mplot3d
import numpy as np
from scipy.interpolate import griddata
from scipy import interpolate
#import numpy.ma as ma
#from numpy.random import uniform, seed

def VDIFF(X,Y,Z,GCP,INTERP):
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
    zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method=INTERP)     
    
    f = interpolate.interp2d(xi, yi, zi, kind=INTERP)
    znew = f(x[0], y[0])
    
    print ("znew=",znew) 


    return znew