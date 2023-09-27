import math
from time import perf_counter
import gdal
import affine
from laspy import file
import numpy as np
from tqdm import tqdm
from numba import jit
import os
import dask.bag as db
import dask.array as da
import datetime

# open byn grid, read as array and get geotransform parameters
g = gdal.Open(R'HT2_2002_CGG2013a\HT2_2002v70_CGG2013a.byn')
b1 = g.ReadAsArray()


# in order to get the pixel value from the byn grid, we need to know the local x,y location of a coordinate on the grid. The below gets the inverse affine transformation to go from coordinates to a local x,y
geotransform = g.GetGeoTransform()

fwd_transform =  \
    affine.Affine.from_gdal(*geotransform)
inv_transform = ~fwd_transform

class ellipsoid:


    def __init__(self, a, b, f):
        ellipsoid.a = a
        ellipsoid.b = b
        ellipsoid.f = f
        ellipsoid.inv_f = 1/f
        ellipsoid.e = math.sqrt(((a**2) - (b**2))/(a**2))
        ellipsoid.e2 = (ellipsoid.e)**2
        ellipsoid.se = math.sqrt(((a**2) - (b**2))/(b**2))
        ellipsoid.se2 = (ellipsoid.se)**2
        ellipsoid.A0 = 1 + ((3/4)*(ellipsoid.e**2)) + \
                            ((45/64)*(ellipsoid.e**4)) + \
                            ((175/256)*(ellipsoid.e**6)) + \
                            ((11025/16384)*(ellipsoid.e**8)) + \
                            ((43659/65536)*(ellipsoid.e**10)) + \
                            ((693693/1048576)*(ellipsoid.e**12))

grs80 = ellipsoid(6378137,  6356752.314140347, 0.003352810681183637418)
# clarke1866 = ellipsoid(6378206.4, 6356583.8, 1/294.978698214)
# wgs84 = None

a = 6378137.0  # semi-major axis
b = 6356752.314140  # semi-minor axis 
f = 1/298.257222101  # inverse flattening
e =  0.0818191910435  # eccentricity
e2 = e**2  # eccentricity squared
se = math.sqrt(((a**2) - (b**2)) / (b**2))  # second eccentricity
se2 = se**2
e_1_x = (1-((1-e2)**(1/2)))/(1+((1-e2)**(1/2)))

# ---------- UTM Constants ----------
k0 = .9996
# Central meridian dictionary in degrees
long0 = {
    'test': -75.0,
    'Z08': -135.0,
    'Z09': -129.0,
    'Z10': -123.0,
    'Z11': -117.0
    }


# ---------- Calculate lat/long ----------
@jit(nopython=True)
def utm2latlong(easting, northing, lambda0, a, e2, se2):
    # Calculate distance along central meridian from latitude of origin
    M = 0 + northing/.9996
    e_1 = (1-((1-e2)**(1/2)))/(1+((1-e2)**(1/2)))
    mu = M/(a*(1-(e2/4)-((3*(e2**2))/64)-((5*(e2**3))/256)))

    lat_1_t1 = (((3*e_1)/2) - ((27*(e_1**3))/32))*(math.sin(2*mu))
    lat_1_t2 = (((21*(e_1**2))/16) - ((55*(e_1**4))/32))*(math.sin(4*mu))
    lat_1_t3 = ((151*(e_1**3))/96)*math.sin(6*mu)
    lat_1_t4 = ((1097*(e_1**4))/512)*math.sin(8*mu)
    lat_1 = mu + lat_1_t1 + lat_1_t2 + lat_1_t3 + lat_1_t4
    
    C_1 = se2*(math.cos(lat_1))**2
    T_1 = math.tan(lat_1)**2
    N_1 = a/((1-(e2*(math.sin(lat_1)**2)))**(1/2))
    R_1 = (a*(1-e2))/((1-(e2*(math.sin(lat_1)**2)))**(3/2))
    D = (easting - 500000)/(N_1*k0)
    
    lat_t1 = ((N_1*math.tan(lat_1))/R_1)
    lat_t2 = (D**2)/2 - (5 + 3*T_1 + 10*C_1 - ((4*C_1)**2) - (9*se2))*((D**4)/24)
    lat_t3 = (61 + 90*T_1 + 298*C_1 + 45*(T_1**2) - 252*se2 - 3*(C_1**2))*((D**6)/720)
    lat = lat_1 - (lat_t1*(lat_t2 + lat_t3))
    
    # lon = math.radians(lambda0) + ((((1 + (2*T_1) + C_1)*((D**3)/6)) + ((5 - 2*C_1 + 28*T_1 - (3*(C_1**2)) + (8*(se2**2)) + (24*(T_1**2)))*((D**5)/120)))/math.cos(lat_1))
    lon_t1 = D - ((1 + 2*T_1 + C_1)*((D**3)/6))
    lon_t2 = 5 - 2*C_1 + 28*T_1 - (3*(C_1**2)) + (8*se2) + 24*(T_1**2)
    lon_t3 = (D**5)/120
    lon = math.radians(lambda0) + ((lon_t1 + lon_t2*lon_t3)/(math.cos(lat_1)))
 
    return math.degrees(lat), math.degrees(lon)


# get elevation value from byn grid with lat, long
def retrieve_pixel_value(lon, lat):
    """Return floating-point value that corresponds to given point."""

    row, col = inv_transform * (lon, lat)

    return b1[int(col), int(row)]*.001

# read las file and return x,y,z array
def read_las(las):
    las = file.File(las, mode='r')
    points = np.column_stack((las.x, las.y, las.z))
    las.close()
    return points

# combine coversion of x,y to lat, long and get elevation value
def grid_elev_from_xy(x,y):
    lat,long = utm2latlong(x, y, long0['Z09'], grs80.a, grs80.e2, grs80.se2)
    byn_elev = retrieve_pixel_value(long, lat)
    return byn_elev

# vertically transform z from the x,y,z array and return transformed points
def vertical_transform(points):
    # vect = np.vectorize(grid_elev_from_xy, otypes=[np.float32])
    # out = vect(points[:,0], points[:,1])
    # points[:,2] += out


    # for idx,(x,y,z) in enumerate(tqdm(points)):
    for idx,(x,y,z) in enumerate(points):

        byn_elev = grid_elev_from_xy(x,y)

        points[idx,2] -= byn_elev
 
    return points

# main function of the program. Reads, transforms and writes new las file
def datum_convert(infile, outdir, low_memory=False):
    filename = os.path.basename(infile).split('.')[0]
    outfile = os.path.join(outdir,filename + '_cgvd2013.las')
    
    las = file.File(infile, mode='r')
    header = las.header
    

    pts = np.column_stack((las.x, las.y, las.z))

    if low_memory:                                  # if memory is limited in processing machine, we can run a very memory friendly version of the transformation. The trade off is speed
        result = vertical_transform(pts)
    else:
        chunks = np.array_split(pts, 200, axis=0)     # split array into n chunks. Determine how many chunks to split each file into TODO
        dbag = db.from_sequence(chunks)                 # TODO determine number of partitions and partition size
        result = np.concatenate(dbag.map(vertical_transform).compute(), axis=0)     # concatenate results into a single array


    outfile = file.File(outfile,mode= "w",          # create output file and copy header from original file. The min and max Z need to changed in the header here TODO
        vlrs = las.header.vlrs,
        header = header)

    for spec in las.reader.point_format:                # for every dimension in the specific point format (ie GPS time, intensity, RGB, whatever), copy that dimension into the new file
        in_spec = las.reader.get_dimension(spec.name)
         
        outfile.writer.set_dimension(spec.name, in_spec)
    

    outfile.z = result[:,2]     # Replace original Z values with new transformed Z values

    outfile.close()
    las.close()


if __name__=='__main__':
    outdir = R'D:\test\lidar_data\out'
    
    # f = R"D:\test\lidar_data\building_sample_classified.las"
    f = R"D:\test\lidar_data\bc_092g043_4_2_1_xyes_8_utm10_2019.las"
    # f = R"D:\test\lidar_data\bc_103P091_1_3_3_xyes_8_utm09_2019.las"
    # f= R"D:\test\lidar_data\2p2_mill_pts.las"



    print(datetime.datetime.now())
    s = perf_counter()
    datum_convert(f,outdir,low_memory=False)
    f = perf_counter()

    print(f-s)



'''TODO
Add grid selection
Add utm zone selection
Edit new las header
Make gui
'''
    