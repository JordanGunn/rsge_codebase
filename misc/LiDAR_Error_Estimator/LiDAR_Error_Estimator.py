import numpy as np
from sympy import Symbol, Matrix, cos, sin, diag



def estimate_lidar_error(A, Cx):

    """
    C = A * Cx * AT
    where:

    C = Estimated error matrix; diagonal components of matrix are estimated errors in  X, Y, Z 
    A = Design matrix (Jacobian of observation equations)
    Cx = Variance-covariance matrix
    AT = Design matrix transposed
    """

    # calculate estimated error
    C = A * Cx * (A.T)

    # format and print results
    print(f'\nSx:\t +|- {C[0,0]**(1/2)}\nSy:\t +|- {C[1,1]**(1/2)}\nSz:\t +|- {C[2,2]**(1/2)}')
    print(f'\nMaximum Radial Magnitude:\t +|- {(C[0,0] + C[1,1] + C[2,2])**(1/2)}')
    print(f'Maximum Horizontal Magnitude:\t +|- {(C[0,0] + C[1,1])**(1/2)}')

    return C


def compute_A(A_symbol_matrix, Xos, Yos, Zos, omegas, phis, kappas, lxs, lys, lzs, alphas, betas, gammas, etas, rs):
    
    """
    Compute and return design matrix A

    input param :: observations > list of observations in the following order: [x, y, z, omega, phi, kappa, lx, ly, lz, alpha, beta, gamma, eta, r]

        where:
            > Xo, Yo, Zo = coordinates values of the position of the mapping frame
            > omega, phi, kappa = instantaneous attitude of the the measuring platform
            > lx, ly, lz = lever arm offsets
            > alpha, beta, gamma = boresighting misalignments
            > eta, r = observation angle and range, respectively

    input param :: Ao > Symbolic Jacobian Matrix (Design matrix A) created from func build_design_matrix()
    """

    # create variables to build symbolic equations ------------
    Xo = Symbol('Xo') # X coordinate of the mapping frame -----
    Yo = Symbol('Yo') # Y coordinate of the mapping frame -----
    Zo = Symbol('Zo') # Z coordinate of the mapping frame -----
    r = Symbol('r') # sigting range ---------------------------
    eta = Symbol('eta') # sighting angle ----------------------
    kappa = Symbol('kappa') # platform attitude; heading/yaw --
    phi = Symbol('phi') # platform attitude; pitch ------------
    omega = Symbol('omega') # platform attitude; roll ---------
    alpha = Symbol('alpha') # boresight misalignment in omega -
    beta = Symbol('beta') # boresight misalignment in phi -----
    gamma = Symbol('gamma') # boresight misalignment in gamma -
    lx = Symbol('lx') # lever arm offset in x -----------------
    ly = Symbol('ly') # lever arm offset in y -----------------
    lz = Symbol('lz') # lever arm offset in z -----------------
    
    # create a list of substitutions for symbolic variables and their corresponding values
    sub = [(Xo, Xos), 
    (Yo, Yos), 
    (Zo, Zos), 
    (omega, omegas), 
    (phi, phis), 
    (kappa, kappas), 
    (lx, lxs), 
    (ly, lys), 
    (lz, lzs), 
    (alpha, alphas), 
    (beta, betas), 
    (gamma, gammas), 
    (eta, etas), 
    (r, rs)
    ]
    
    # perform substitution
    A = Ao.subs(sub)

    return A


def build_Cx(Sx, Sy, Sz, S_omega, S_phi, S_kappa, S_lx, S_ly, S_lz, S_alpha, S_beta, S_gamma, S_eta, S_r):

    """
    Builds variance-covariance matrix; a square matrix with diagonal elements consisting of observation uncertainty values
    """

    # assign precisions of system components to array and square the values to calculate variance
    Cx_flat = np.array([
        Sx, 
        Sy, 
        Sz, 
        S_omega, 
        S_phi, 
        S_kappa, 
        S_lx, 
        S_ly, 
        S_lz, 
        S_alpha, 
        S_beta, 
        S_gamma, 
        S_r, 
        S_eta
        ]) ** 2
    
    # create square diagonal matrix of system component variances
    Cx0 = np.diag(Cx_flat)
    
    # convert to sympy Matrix object
    Cx = Matrix(Cx0)
    
    return Cx


def build_design_matrix(R_opk, lever_xyz, R_abg):

    """ 
    Builds and returns design matrix (A) using symbolic variables

    input param :: R_opk > Rotation matrix about omega, phi, kappa (instantaneous aircraft attitude)
    input param :: lever_xyz > lever-arm offset vector 
    input param :: R_abg > Rotation matrix about alpha, beta, gamma (boresighting misalignments)

    A = [A_xyz (3x3) :: A_opk (3x3) :: A_lever_xyz (3x3) :: A_abg (3x3) :: A_sar (3x2)]
    
    """
    
    # create variables to build symbolic equations ------------
    Xo = Symbol('Xo') # X coordinate of the mapping frame -----
    Yo = Symbol('Yo') # Y coordinate of the mapping frame -----
    Zo = Symbol('Zo') # Z coordinate of the mapping frame -----
    r = Symbol('r') # sigting range ---------------------------
    eta = Symbol('eta') # sighting angle ----------------------
    kappa = Symbol('kappa') # platform attitude; heading/yaw --
    phi = Symbol('phi') # platform attitude; pitch ------------
    omega = Symbol('omega') # platform attitude; roll ---------
    alpha = Symbol('alpha') # boresight misalignment in omega -
    beta = Symbol('beta') # boresight misalignment in phi -----
    gamma = Symbol('gamma') # boresight misalignment in gamma -
    lx = Symbol('lx') # lever arm offset in x -----------------
    ly = Symbol('ly') # lever arm offset in y -----------------
    lz = Symbol('lz') # lever arm offset in z -----------------

    # transformation matrix, change direction of z
    R_ref = Matrix([
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, -1]
    ])

    # initial position of the mapping frame (ie GNSS noise)
    A_xyz = Matrix([
        [Xo], 
        [Yo], 
        [Zo]
    ])

    # projection of system parameters to the ground (vector)
    A_sar_des = Matrix([
        [0],
        [-1*r*sin(eta)], 
        [r*cos(eta)]
     ])
     
    # create observation equations
    A_obs = A_xyz + (R_ref * R_opk) * (lever_xyz + (R_abg * A_sar_des))
    
    # create a list of variables to take partial derivatives
    A_obs_deriv = Matrix([
        Xo, 
        Yo, 
        Zo, 
        omega, 
        phi, 
        kappa, 
        lx, 
        ly, 
        lz, 
        alpha, 
        beta, 
        gamma, 
        eta, 
        r
        ])
    
    # take partial derivatives
    Ao = A_obs.jacobian(A_obs_deriv)

    return Ao


def build_R_opk():
    
    # Create variables to build symbolic equations
    kappa = Symbol('kappa') # platform attitude; heading/yaw
    phi = Symbol('phi') # platform attitude; pitch
    omega = Symbol('omega') # platform attitude; roll

    # create rotation matrix for aircraft attitude at hypothetical instantaneous point of observation
    R_opk = Matrix([
        [cos(kappa)*cos(phi), -1*sin(kappa)*cos(omega)+cos(kappa)*sin(phi)*sin(omega), sin(kappa)*sin(omega)+cos(kappa)*sin(phi)*cos(omega)],
        [sin(kappa)*cos(phi), cos(kappa)*cos(omega)+sin(kappa)*sin(phi)*sin(omega), -1*cos(kappa)*sin(omega)+sin(kappa)*sin(phi)*cos(omega)],
        [-1*sin(phi), cos(phi)*sin(omega), cos(phi)*cos(omega)]
    ])

    return R_opk

def build_R_abg():

    # Create variables to build symbolic equations
    alpha = Symbol('alpha') # boresight misalignment in omega
    beta = Symbol('beta') # boresight misalignment in phi
    gamma = Symbol('gamma') # boresight misalignment in gamma

    # create rotation matrix for boresight misalignments
    R_abg = Matrix([
        [cos(gamma)*cos(beta), sin(gamma)*cos(alpha)+cos(gamma)*sin(beta)*sin(alpha), sin(gamma)*sin(alpha)-cos(gamma)*sin(beta)*cos(alpha)], 
        [-1*sin(gamma)*cos(beta), cos(gamma)*cos(alpha)-sin(gamma)*sin(beta)*sin(alpha), cos(gamma)*sin(alpha)+sin(gamma)*sin(beta)*cos(alpha)],
        [sin(beta), -1*cos(beta)*sin(alpha), cos(beta)*cos(alpha)]
    ])

    return R_abg

def build_lever_xyz():

    # Create variables to build symbolic equations
    lx = Symbol('lx')
    ly = Symbol('ly')
    lz = Symbol('lz')

    # Create symbolic vector for lever-arm offset parameters
    lever_xyz = Matrix([
        [lx],
        [ly],
        [lz]
    ])

    return lever_xyz


# test the code
Cx = build_Cx(.05, .05, .075, .0000873, .0000873, .000139, .02, .02, .02, .0000175, .0000175, .0000698, .02, .0000768) # Build variance-covariance matrix
R_abg = build_R_abg() # build rotation matrix for boresight misalignment parameters
R_opk = build_R_opk() # build rotation matrix for aircraft attitude parameters
lever_xyz = build_lever_xyz() # build lever-arm offset vector
Ao = build_design_matrix(R_opk, lever_xyz, R_abg) # build symbolic jacobian design matrix
A = compute_A(Ao, .05, .05, .08, 0, 0, 0, -.5, -.5, -.5, .0349066, .0349066, .0349066, 0, 1500) # input values into design matrix and evaluate

C = estimate_lidar_error(A, Cx) # calculate estimated error
