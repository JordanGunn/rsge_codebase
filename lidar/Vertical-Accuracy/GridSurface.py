# Import libraries
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
 
def GridSurf(XX,YY,ZZ,GCP): 
    # Creating dataset
    x = np.array(XX).T#DATA[:,0]
    y = np.array(YY).T#DATA[:,1]
    z = np.array(ZZ).T#DATA[:,2]
    def fun(x, y):
        return x**2 + y

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = y = np.arange(-3.0, 3.0, 0.05)
    
    X, Y = np.meshgrid(x, y)
    zs = np.array(fun(np.ravel(X), np.ravel(Y)))
    Z = zs.reshape(X.shape)
    print("zs=\n",zs)
    print("X=\n",X.shape)
    print("Y=\n",Y.shape)
    print("Z=\n",Z.shape)
    print("Z=\n",Z)

    ax.plot_surface(X, Y, Z)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')