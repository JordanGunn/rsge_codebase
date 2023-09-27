# Create TIN surface plot a 3D surface from  points
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy
from numpy.random import randn
from scipy import array, newaxis
from mpl_toolkits import mplot3d
def TIN_(x,y,z):


    Xs = numpy.array(x).T#DATA[:,0]
    Ys = numpy.array(y).T#DATA[:,1]
    Zs = numpy.array(z).T#DATA[:,2]
    print ("\n\nXs=",Xs)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_trisurf(Xs-Xs.mean(), Ys-Ys.mean(), Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)

    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))

    fig.tight_layout()
    plt.show()

    return surf