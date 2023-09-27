import math
from time import perf_counter
# For projections in the Transverse Mercator Group, the parameters which are required to compeltely and unamgibuously define the projection method are:
# Latitude of natural origin = lat0
# Longitude of natural origin (central meridian) = long0
# Scale factor of natural origin (on the central meridian) = k0
# False easting = FE
# False northing = FN

E = 577274.99
N = 69740.50 
k0 = .9996012717

# ------ WGS84 Ellipsoid Constants -----

# a = 6378137.0  # semi-major axis
# b = 6356752.314140  # semi-minor axis 
# f = 298.257222100882711  # inverse flattening
# e = math.sqrt(6.69437999014*(10**-3))

a = 6377563.396  # semi-major axis
b = 6356752.314140  # semi-minor axis 
f = 1/299.32496  # inverse flattening
e = math.sqrt(0.00667054)

# ----- UTM Constants -----

FE = 400000.00  # False easting
FN = -100000.00 # False northing
lat0 = 49.0  # origin of latitude in degrees
# Central meridian dictionary in degrees
long0 = {
    'test': -2.0,
    'Z08': -135.0,
    'Z09': -129.0,
    'Z10': -123.0,
    'Z11': -117.0
    }


def calculate_constants(f, a):
    n = f/(2-f)
    B = (a/(1+n))*(1+((n**2)/4)+((n**4)/64))

    h1 = n/2 - (2/3)*(n**2) + (37/96)*(n**3) - (1/360)*(n**4)
    h2 = (1/48)*(n**2) + (1/15)*(n**3) - (437/1440)*(n**4)
    h3 = (17/480)*(n**3) - (37/840)*(n**4)
    h4 = (4397/161280)*(n**4)

    return B, h1, h2, h3, h4, n


def calculate_lat_long(E, FE, N, FN, k0, B, h1, h2, h3, h4, e, long0):
    # initial approximations for meta coordinates
    eta_prime = (E - FE) / (B * k0) 
    xi_prime = ((N - FN) + (k0*5429228.602)) / (B * k0)

    # approximate meta coordinates
    approx_eta = {}
    approx_xi = {}
    for i, (x, h) in enumerate(zip([2, 4, 6, 8], [h1, h2, h3, h4])):
        approx_xi[f'xi{i+1}_prime'] = h*(math.sin(x*xi_prime))*(math.cosh(x*eta_prime))
        approx_eta[f'eta{i+1}_prime'] = h*(math.cos(x*xi_prime))*(math.sinh(x*eta_prime))



    xi_prime0 = xi_prime - sum(approx_xi.values())
    eta_prime0 = eta_prime - sum(approx_eta.values())

    # calculate beta prime
    beta_prime = math.asin(math.sin(xi_prime0)/math.cosh(eta_prime0))
    
    # approximate Q prime
    Q_prime = math.asinh(math.tan(beta_prime))
    

    diff = 1
    threshold = .000000001
    
    # Qpp = Q_prime + e*math.atanh(e*math.tanh(Q_prime))
    # Qppp = Q_prime + e*math.atanh(e*math.tanh(Qpp))
    # Qpppp = Q_prime + e*math.atanh(e*math.tanh(Qppp))
    # Qppppp = Q_prime + e*math.atanh(e*math.tanh(Qpppp))
    # print(Q_prime,Qpp,Qppp,Qpppp,Qppppp)

    _qpp = Q_prime + e*math.atanh(e*math.tanh(Q_prime))
    while diff > threshold:
        q = Q_prime + e*math.atanh(e*math.tanh(_qpp))
        diff = abs(_qpp-q)
        _qpp = q
        # print(_qpp)
        
    # print('Q prime is: ', Qppppp - Qpppp)
    # while abs(diff) > threshold:
    #    print(diff)
    #    Qpp = Q_prime + e*math.atanh(e*math.tanh(Q_prime))
    #    diff = Qpp - Q_prime
    #    Q_prime = Qpp
    #    print(diff)

    lat = math.atan(math.sinh(_qpp))
    long = math.radians(long0) + math.asin(math.tanh(eta_prime0)/math.cos(beta_prime))

    return math.degrees(lat), math.degrees(long)


def main():
    B, h1, h2, h3, h4, n = calculate_constants(f, a)
    lat, long = calculate_lat_long(E, FE, N, FN, k0, B, h1, h2, h3, h4, e, long0['test'])
    # print(lat,long)


if __name__ == '__main__':
    s = perf_counter()
    main()
    f = perf_counter()
    print(f - s)






