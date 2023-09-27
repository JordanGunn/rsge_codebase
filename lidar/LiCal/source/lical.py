# ------------------------------------------------------------------------------
# LiCal
# Written by Graeme Prendergast, Brett Edwards, and Natalie Jackson, GeoBC
# ------------------------------------------------------------------------------
# TODO:
# - clean up script: functionize where possible!
# - make better output for insufficient overlap case
# - chi table not populating with correct values
# - update chi test (i.e., change binning method, etc.)
# !     - See chisquareTest_func_nj.py for a sandbox of trying to solve
# !         the problems in chisquare_test()
# ------------------------------------------------------------------------------

import datetime
import random
import base64
import math
import csv
import sys
import os
import shutil
from unicodedata import decimal
# from unittest import result
import tqdm
from halo import Halo

# from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    BaseDocTemplate,
    Table,
    TableStyle,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Frame,
    FrameBreak,
    PageBreak
)
from reportlab.lib import colors
from PyPDF2 import PdfFileMerger, PdfFileReader
import scipy.stats as stats
# from scipy import spatial

import numpy as np
import laspy

from shapely.geometry import Polygon
from matplotlib import path as mpltPath
from scipy.spatial import ConvexHull, cKDTree
from pathlib import Path

from itertools import combinations, chain
import struct

import config

import warnings
warnings.filterwarnings(
    "ignore",
    "(?s).*MATPLOTLIBDATA.*",
    category=UserWarning
)

# Initialize polygon cache dictionary
polygon_cache = {}

# Formatting variable for terminal output
dashline = config.dashline


def main():
    """
    Run LiCal from command line.
    """
    print(dashline)
    input_dir = input("Path to input directory: ")
    output_dir = input("Path to output directory: ")
    company_name = input("Company name: ")

    sample_size = config.TEST_SAMPLE_SIZE
    v_rmse_thresh = config.V_RMSE_THRESH
    h_rmse_thresh = config.H_RMSE_THRESH
    recurse = False

    run_batch_lical(
        input_dir,
        output_dir,
        company_name,
        sample_size,
        v_rmse_thresh,
        h_rmse_thresh,
        recurse
    )


def run_batch_lical(
    indir,
    outdir,
    company_name,
    sample_size,
    v_rmse_thresh,
    h_rmse_thresh,
    recurse=True,
    queue_item=None
):
    """
    Function called by LiCal GUI.
    """
    start_time = datetime.datetime.now()

    inpath = Path(indir)

    if recurse:
        las_files = inpath.rglob('*.las')
        laz_files = inpath.rglob('*.laz')
        lidar_files = chain(las_files, laz_files)
    else:
        las_files = inpath.glob('*.las')
        laz_files = inpath.glob('*.laz')
        lidar_files = chain(las_files, laz_files)

    combos = list(combinations(lidar_files, 2))

    chisquareResults = []

    if queue_item:
        intro_message = f"queue item {queue_item} "
    else:
        intro_message = ""
    print(
        f"{dashline}"
        f"{config.AnsiColors.yellow}"
        f"\nLiCal {intro_message}started {print_friendly_time(start_time)}"
    )

    for count, pair in enumerate(combos):
        print(
            f"{config.AnsiColors.white}"
            f"{dashline}"
            f"Swath pair {count + 1} of {len(combos)}:\n",
            flush=True
        )
        try:
            chisquareResults.append(
                compare_swath_pair(
                    pair[0],
                    pair[1],
                    outdir,
                    start_time,
                    company_name,
                    sample_size,
                    v_rmse_thresh,
                    h_rmse_thresh
                )
            )
        except Exception as e:
            print(e)
            continue

    if chisquareResults:
        make_chi_table(
            chisquareResults,
            company_name,
            outdir
        )
    else:
        insufficient_overlap_report(
            outdir,
            indir
        )

    _delete_temp_dir(
        outdir
    )

    # Find run duration and truncate at 10-millisecond decimal place
    lical_runtime = print_friendly_duration(
        datetime.datetime.now() - start_time
    )

    if queue_item:
        outro_message_0 = f"Queue item {queue_item}"
        outro_message_1 = ""
    else:
        outro_message_0 = "LiCal"
        outro_message_1 = (
            "\n\nResults saved here:"
            f"\n\t{config.AnsiColors.yellow}{outdir}"
            f"{config.AnsiColors.reset}"
            f"{dashline}"
        )
    print(
        f"{dashline}"
        f"{outro_message_0} runtime: {lical_runtime}"
        f"{outro_message_1}"
    )


def insufficient_overlap_report(outdir, indir):
    """
    Write a text file to the output location
    alerting there was insufficient swath
    overlap to run LiCal.
    """
    insufficient_overlap_txt_report = os.path.join(
        outdir,
        "LiCal_insufficient_swath_overlap.txt"
    )

    with open(insufficient_overlap_txt_report, "w") as txt:
        txt.write(
            f"The swaths in {indir} have insufficient overlap "
            f"in regions of flat (level) or sloped surfaces "
            f"for LiCal to assess interswath accuracy."
        )


def compare_swath_pair(
    fp1,
    fp2,
    outdir,
    start_time,
    company_name,
    sample_size,
    v_rmse_thresh,
    h_rmse_thresh
):
    """
    Compare two lidar files for vertical alignment
    and save results to the provided output directory (outdir).
    """
    calc_residual_start = datetime.datetime.now()

    flat_residuals, slope_residuals, all_residuals, N = calculate_residuals(
        fp1,
        fp2,
        sample_size
    )

    calc_residual_runtime = print_friendly_duration(
        datetime.datetime.now() - calc_residual_start
    )
    print(
        f"{config.AnsiColors.cyan}"
        f"Residual calculation runtime: "
        f"({calc_residual_runtime})\n"
        "Residuals calculated!"
        f"{config.AnsiColors.reset}",
        flush=True
    )

    assert (len(flat_residuals) > 0 and len(slope_residuals) > 0), (
        "The overlap of the given swaths is too small.")

    test_results = analyze_residuals(
        flat_residuals,
        slope_residuals,
        all_residuals,
        N,
        v_rmse_thresh,
        h_rmse_thresh
    )

    chisquareResults = chisquareTest(test_results)

    test_results['chi-square'] = chisquareResults

    output_results(
        test_results,
        save_info=(
            outdir,
            start_time,
            fp1,
            fp2,
            company_name,
            v_rmse_thresh,
            h_rmse_thresh
        )
    )

    # Delete the temp image files
    _delete_temp_png_files(outdir)

    chisquareResults.insert(0, f'{os.path.split(fp1)[1]}\n{os.path.split(fp2)[1]}')

    return chisquareResults


def chisquareTest(test_results):
    # ! See chisquareTest_func_nj.py for a sandbox of trying to make this function work properly
    values = test_results['all_residuals']
    values = np.array(values)
    numOfSamples = len(values)
    mean = values.mean()
    stdev = values.std(ddof=1)
    # print(f'{mean=}')
    # print(f'{stdev=}')
    valRange = max(values) - min(values)
    # print(f'{valRange=}')
    initWidth = round(valRange / (1 + 3.22 * (math.log10(len(values)))), 10)
    # print(f'{initWidth=}')
    initBins = round(valRange / initWidth)
    # print(f'{initBins=}')
    binWidth = valRange / initBins
    # print(f'{binWidth=}')
    numOfBins = round(valRange / binWidth)
    # print(f'{numOfBins=}')
    bounds = []
    normalProbability = []
    predictedFreq = []
    observedFreq = []
    chiSquare = []
    bounds.append(min(values))
    for i in range(numOfBins):
        bounds.append(round(bounds[i] + binWidth, 10))
        normalProbability.append(
            stats.norm.cdf(
                bounds[i + 1],
                mean,
                stdev
            ) - stats.norm.cdf(
                bounds[i],
                mean,
                stdev
            )
        )
        predictedFreq.append(normalProbability[i] * numOfSamples)
        if i == numOfBins - 1:
            observedFreq.append(sum(num >= bounds[i] and num <= bounds[i + 1] for num in values))
        else:
            observedFreq.append(sum(num >= bounds[i] and num < bounds[i + 1] for num in values))
        chiSquare.append(
            (predictedFreq[i] - observedFreq[i]) ** 2 / predictedFreq[i]
        )

    chiSum = sum(chiSquare)
    pValue = stats.chi2.sf(chiSum, numOfBins - 1)

    return [
        chiSum,
        numOfBins - 1,
        max(values),
        min(values),
        valRange,
        pValue
    ]


def calculate_residuals(
    fp1,
    fp2,
    sample_size,
    verbose=False
):
    """
    Calculate a set of data quality measurements between point clouds.

    Currently, we pick a random sample of points from point cloud #2,
    and then for each point, we find its nearest neighborhood of points
    in cloud #1. We fit a plane to this neighborhood using principle
    component analysis, then decide if the plane is in fact an accurate
    surface model using eigenvalue analysis. If it is, we then compute
    the point-to-plane distance for a residual measurement.

    Args:
        fp1 : File path to the first .las/.laz file
        fp2 : File path to the second .las/.laz file
        verbose : Flag to provide additional information
    Returns:
        flat_residuals : An array of residuals from flat regions
        slope_residuals : An array of residuals from sloped regions
        N : An array of normal vectors corresponding to each measurement
            in slope_residuals ONLY, ie, N[i] <=> slope_residuals[i]
    """
    points1, points2 = get_lidar_points(fp1, fp2, verbose=False)

    halo_spinner = Halo(
        text="Sorting points...",
        text_color="cyan"
    )
    halo_spinner.start()

    # Randomly permute our lidar points
    # las files often contain subset of points that are in a line,
    # so this helps our k-d tree nice and balanced.
    np.random.shuffle(points1)
    np.random.shuffle(points2)

    # Manual error simulation goes here if wanted

    nn_tree = cKDTree(points1)


    # Reshape the tree data in order for pykdtree to work. Not needed with cKDTree
    # tree_data = nn_tree.data.reshape((nn_tree.n, nn_tree.ndim))

    N = []
    flat_residuals = []
    slope_residuals = []
    all_residuals = []
    test_indices = random.sample(
        range(len(points2)),
        int(len(points2) / (100 / sample_size))
    )

    # Stop terminal spinner and print complete statement
    halo_spinner.stop()
    print(
        f"{config.AnsiColors.cyan}"
        f"Points sorted!"
        f"{config.AnsiColors.reset}"
    )

    if len(test_indices) < 20_000:
        raise ValueError("Not enough sample points found")

    print(
        f"{config.AnsiColors.cyan}"
        "Calculating residuals...",
        flush=True
    )

    # Loop through the test points
    for test_index in tqdm.tqdm(test_indices):
        test_point = points2[test_index]

        # Reshape the test point in order for pykdtree to work. Not needed with cKDTree
        # _test_point = test_point.reshape(1,-1)

        nn = 25
        # Search for the k nearest neighbors of test_point
        nn_distances, nn_indices = nn_tree.query(test_point, k=nn)

        neighborhood = np.array([nn_tree.data[i] for i in nn_indices])
        # Reshape the nerighborhood points in order for pykdtree to work. Not needed with cKDTree
        # neighborhood = neighborhood.reshape((nn,3))

        # Center the test point and neighborhood around the origin
        mean_vector = np.mean(neighborhood, axis=0)
        neighborhood -= mean_vector
        test_point -= mean_vector

        # Performing the principal component analysis
        surface_cov = np.cov(np.transpose(neighborhood))  # Covariance Matrix
        eigenvalues, eigenvectors = np.linalg.eig(surface_cov)  # Eigenstuff
        eigen_dict = {eigenvalues[i]: eigenvectors[:, i] for i in range(0, 3)}

        if verbose:
            print("\nEigendictionary:")
            for entry in eigen_dict:
                print(f"{entry} : {eigen_dict[entry]}")
            print()

        # The eigenvector belonging to the smallest eigenvalue
        # is the normal vector of our best fit plane
        normal = eigen_dict[min(eigen_dict)]

        if surface_is_planar(eigenvalues, verbose=verbose):
            dist = point_to_plane_distance(test_point, normal)

            # Filter out obvious outliers (>1meter). It'd be nice to just rely
            # on remove_outliers(), but we need this for oddly-shaped swaths.
            if abs(dist) <= 100:
                angle = np.arccos(normal[2]) * (180 / math.pi)
                if angle > 90:
                    angle -= 180

                if verbose:
                    print(f"Neighborhood angle: {angle}")
                # append all to one list for chi-test
                # Bin the residual based on its region's slope
                if abs(angle) <= 5:
                    flat_residuals.append(dist)
                    if verbose:
                        print(f"{dist} recorded to Flat")
                elif abs(angle) >= 10:
                    slope_residuals.append(dist)
                    N.append(normal)
                    if verbose:
                        print(f"{dist} recorded to Sloped")
                all_residuals.append(dist)
        if verbose:
            plot_3d(neighborhood, normal, test_point)

    if (
        len(flat_residuals) < config.SAMPLE_NUM_THRESHOLD
        and len(slope_residuals) < config.SAMPLE_NUM_THRESHOLD
    ):
        raise ValueError("Not enough valid residuals found")

    halo_spinner.stop()

    return (
        np.array(flat_residuals),
        np.array(slope_residuals),
        np.array(all_residuals),
        np.array(N)
    )


def surface_is_planar(eigenvalues, verbose=False):
    """
    Check if some eigenvalues describe a reasonably planar surface.

    This method of planarity verification is explained in the ASPRS
    article "Guidelines on Geometric Inter-Swath Accuracy and Quality
    of Lidar Data", doi: 10.14358/PERS.84.3.117

    Args:
        eigenvalues : A set of principle component eigenvalues
        verbose : Flag to provide additional information
    Returns:
        A boolean value, True <=> the surface is reasonably planar
    """
    eigenvalues.sort()

    ratio1 = eigenvalues[1] / eigenvalues[2]
    ratio2 = eigenvalues[0] / sum(eigenvalues)
    if verbose:
        print(f"L2 / L1 = {ratio1}")
        print(f"L3 / (L1 + L2 + L3) = {ratio2}")

    # These ratio thresholds are modified slightly from the ASPRS version
    if ratio1 > 0 and ratio2 < 0.004:
        if verbose:
            print("PASSED planarity test\n")
        return True
    else:
        if verbose:
            print("FAILED planarity test\n")
        return False


def point_to_plane_distance(point, norm):
    """
    Calculate the orthogonal distance from a point to a plane.

    This distance measurement is done in R^3. Further, we assume that
    the point and plane have been centered around the origin (0,0,0).
    There is some discussion as to whether or not we should allow
    negative distances, but currently we are. If in future we want to
    only allow positive distances, use: k = abs(...)

    Args:
        point : A vector [x,y,z] that describes the point
        norm : The normal vector [x,y,z] that describes the plane
    Returns:
        An orthogonal point-to-plane distance measurement
    """

    k = (norm[0] * point[0]) + (norm[1] * point[1]) + (norm[2] * point[2])
    rescale = math.sqrt(np.dot(norm, norm))

    point_to_plane_dist = k / rescale

    return point_to_plane_dist


def remove_outliers(data, partner=None):
    """
    Remove statistical outliers from a dataset.

    This function uses median absolute deviation as a robust way to
    identify which residual measurements are outliers.

    Args:
        data : A 1-d numpy array of n random variables
    Returns:
        A copy of the data array with outliers removed
    """
    data_median = np.median(data)
    sigma_mad = np.median(np.absolute(data - data_median))
    data_zscore = np.absolute((data - data_median) / sigma_mad)

    filtered_data = data[data_zscore <= 7]

    if partner is not None:
        filtered_partner = partner[data_zscore <= 7]
        return filtered_data, filtered_partner
    else:
        return filtered_data


def get_convex_hull(filename, points_array):
    """
    Check the polygon_cache dict to see if
    this file has already been loaded and
    has a convex hull in the dict.

    If not, create the convex hull
    and add it to the polygon_cache dict.
    """
    if filename in polygon_cache:
        hull = polygon_cache[filename]
    else:
        # Remove z dimension from array
        # and sample every 1000th point
        # making a convex hull
        points_for_hull = points_array[::10000]
        hull = create_hull_polygon(points_for_hull[:, :2])
        polygon_cache[filename] = hull

    return hull


def get_lidar_points(fp1, fp2, verbose=False):
    """
    Grab the point coordinate data from 2 lidar files.

    Two extra things are happening behind the scenes in this function:
    First, we calculate the region of overlap between the two swaths,
        then we filter out any points NOT in that region. This assumes
        all swaths are perfectly rectangular, which is a bad assumption,
        but we have a bandaid fix later to get rid of obvious outliers
        that result from oddly-shaped lidar swaths.
    Second, we filter out any non single-return points to try to make
        our surface modeling more accurate. The ASPRS emphasizes the
        importance of only using single-return points when measuring
        inter-swath accuracy.

    Args:
        fp1 : A filepath to the first lidar file to read and filter
        fp2 : A filepath to the second lidar file to read and filter

    Returns:
        Two (n x 3) numpy arrays of point coordinates in centimeters
    """
    try:
        # sys._MEIPASS is a hidden temp folder used by PyInstaller, it's
        # where the libraries get reassmbled to. If we're not using the
        # PyInstaller executable, sys._MEIPASS will be undefined.
        meipass = sys._MEIPASS
        if meipass not in os.environ["PATH"]:
            os.environ["PATH"] += (os.pathsep + sys._MEIPASS)
    except Exception:
        pass

    # Before taking the time to open the points,
    # let's see if we have their hulls stored and check
    # if they overlap.
    # Should save some time, especially if decompression needs to be done.

    filename1 = os.path.basename(fp1)
    filename2 = os.path.basename(fp2)

    # Create bounding boxes from the header of each lidar file
    header1 = parse_header(fp1)
    a = BoundingBox(
        header1['xmin'],
        header1['xmax'],
        header1['ymin'],
        header1['ymax']
    )

    header2 = parse_header(fp2)
    b = BoundingBox(header2['xmin'], header2['xmax'],
                    header2['ymin'], header2['ymax'])

    # Calculate bounding box of the overlapping region
    ab = BoundingBox(
        max(a.xmin, b.xmin),
        min(a.xmax, b.xmax),
        max(a.ymin, b.ymin),
        min(a.ymax, b.ymax)
    )

    # If the two lidar swaths intersect:
    if ((ab.xmax - ab.xmin > 0) and (ab.ymax - ab.ymin > 0)):

        if filename1 in polygon_cache and filename2 in polygon_cache:
            hull1 = polygon_cache[filename1]
            hull2 = polygon_cache[filename2]

            if not hull1.intersects(hull2):
                # If swaths don't intersect, raise an error
                # and move on to the next pair of files
                raise ValueError("The lidar swaths do not overlap.")

        try:
            with Halo(
                text="Reading/decompressing lidar files...",
                text_color="cyan"
            ):
                infile1 = laspy.read(fp1, laz_backend=laspy.LazBackend.LazrsParallel)
                infile2 = laspy.read(fp2, laz_backend=laspy.LazBackend.LazrsParallel)

            print(
                f"{config.AnsiColors.cyan}"
                f"Files decompressed/read!"
                f"{config.AnsiColors.reset}"
            )
        except Exception:
            raise FileNotFoundError(
                "Error opening one or both of the lidar files. "
                "Please check that both file paths are correct."
            )

        # Read the raw (X,Y,Z) values for each point in both clouds
        points1 = np.column_stack((infile1.x, infile1.y, infile1.z))
        points2 = np.column_stack((infile2.x, infile2.y, infile2.z))

        # Check polygon_cache dict to see if we've loaded this file
        # and stored its convex hull.
        # If not, create one and store it.
        hull1 = get_convex_hull(filename1, points1)
        hull2 = get_convex_hull(filename2, points2)

        # Check if swaths overlap
        if hull1.intersects(hull2):

            # Get only the single returns from each file
            return_filter1 = infile1.num_returns == 1
            return_filter2 = infile2.num_returns == 1

            filtered_points1 = points1[return_filter1]
            filtered_points2 = points2[return_filter2]

            # If hulls overlap, find intersecting polygon
            intersect = find_polygon_intersection(hull1, hull2)

            # Filter points within the overlap area
            points_inside1, points_inside2 = get_points_in_polygon(
                intersect,
                filtered_points1,
                filtered_points2
            )

            # Show a plot of the 2 polygons and their intersecting area
            if verbose:
                show_intersection(hull1, hull2, intersect)

        else:  # We can't make any measurements if there is no overlap
            raise ValueError(no_overlap_message())

    else:  # We can't make any measurements if there is no overlap
        raise ValueError(no_overlap_message())

    # Convert to centimeters because I hate dealing with lists of
    # floats that are exclusively < 1. We'll change back later on.
    return points_inside1 * 100, points_inside2 * 100


def no_overlap_message():
    no_overlap_message = (
        "\n\tThis pair of lidar swaths do not overlap; "
        "\n\tcannot compare interswath accuracy."
    )
    return no_overlap_message


def get_points_in_polygon(polygon, points1, points2):
    """
    Get points from both sets of points, from the polygon provided

    Args:
        polygon : Shapely polygon object
        points1 : array(n x 3) of x,y,z point data
        points2 : array(n x 3) of x,y,z point data
    Returns:
        Two (n x 3) arrays of points inside the polygon. One for each input array.
    """
    polygon_array = np.array(polygon.exterior.coords)

    intersection = mpltPath.Path(polygon_array)

    points_inside_filter1 = intersection.contains_points(points1[:, :2])
    points_inside_filter2 = intersection.contains_points(points2[:, :2])

    points_inside1 = points1[points_inside_filter1]
    points_inside2 = points2[points_inside_filter2]

    return points_inside1, points_inside2


def create_hull_polygon(points):
    """
    Create a Shapely polygon that represents the Convex Hull of the provided points

    Args:
        points : array(n x 2) of x,y point data
    Returns:
        Shapely polygon object
    """
    try:
        hull = ConvexHull(points)
    except Exception:
        raise ValueError("Not enough points in las file")

    xy_vertices = np.vstack(points[hull.vertices])

    polygon = Polygon(xy_vertices)

    return polygon


def find_polygon_intersection(polygon1, polygon2):
    """
    Find the intersecting area between 2 Shapely polygons

    Args:
        polygons 1 & 2: Shapely polygon objects
    Returns:
        Shapely polygon object
    """
    intersect = polygon1.intersection(polygon2)

    return intersect


def show_intersection(Polygon1, Polygon2, Intersection):
    """Graphically plot 3 Shapely polygons"""

    plt.plot(*Polygon1.exterior.xy, 'r-')
    plt.plot(*Polygon2.exterior.xy, 'g-')
    plt.fill(*Intersection.exterior.xy, 'b', alpha=0.5)

    plt.show()


def plot_3d(points, normal, test_point):
    """Graphically plot some geometry in R^3."""
    fig = plt.figure()
    fig.set_size_inches(12, 10)
    ax = plt.subplot(projection='3d')

    # Plot the points
    X = points[:, 0]
    Y = points[:, 1]
    Z = points[:, 2]
    ax.scatter(X, Y, Z)
    ax.scatter(
        test_point[0],
        test_point[1],
        test_point[2],
        color='red'
    )

    # Compute and plot the plane
    d = 0
    xx, yy = np.meshgrid(
        range(
            np.int32(min(X)),
            np.int32(max(X)),
            25
        ),
        range(
            np.int32(min(Y)),
            np.int32(max(Y)),
            25
        )
    )

    zz = ((-normal[0] * xx) - (normal[1] * yy) - d) * 1. / normal[2]

    ax.plot_surface(
        xx,
        yy,
        zz,
        color='yellow',
        alpha=0.5
    )

    # Force the same aspect ratio for all axes
    max_range = max(
        np.array(
            [
                max(X) - min(X),
                max(Y) - min(Y),
                max(Z) - min(Z)
            ]
        )
    ) / 2.0
    mid_x = (max(X) + min(X)) * 0.5
    mid_y = (max(Y) + min(Y)) * 0.5
    mid_z = (max(Z) + min(Z)) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    plt.show()


def analyze_residuals(
    flat_residuals,
    slope_residuals,
    all_residuals,
    N,
    v_rmse_thresh,
    h_rmse_thresh
):
    """
    Calculate some statistics from residual measurements.

    Args:
        flat_residuals : Residuals from flat regions
        slope_residuals : Residuals from sloping regions
        N : Normal vectors corresponding to each slope residual length
    Returns:
        A dictionary containing a collection of statistics/errors
    """
    flat_residuals = remove_outliers(flat_residuals)
    slope_residuals, N = remove_outliers(slope_residuals, partner=N)
    all_residuals = remove_outliers(all_residuals)

    if (
        len(flat_residuals) < config.SAMPLE_NUM_THRESHOLD
        and len(slope_residuals) < config.SAMPLE_NUM_THRESHOLD
    ):
        raise ValueError("Not enough valid residuals found.")

    # This is a tricky bit of stats to estimate horizontal offset.
    # Refer to the ASPRS article on inter-swath lidar accuracy testing
    # for a full explanation and derivation.
    N_xy, N_z = N[:, :2], N[:, 2]
    D_r = slope_residuals - (N_z * np.mean(slope_residuals))
    delta_h = np.linalg.lstsq(N_xy, D_r, rcond=None)

    results = {
        'flat_residuals': flat_residuals,
        'slope_residuals': slope_residuals,
        'all_residuals': all_residuals,
        'offset_vector': delta_h[0],
        'ov_length': math.sqrt(delta_h[0][0] ** 2 + delta_h[0][1] ** 2),
        'ov_rmsd': math.sqrt(delta_h[1][0] / len(slope_residuals)),
        'flat_mean': np.mean(flat_residuals),
        'flat_median': np.median(flat_residuals),
        'flat_std': np.std(flat_residuals),
        'flat_95p': (
            np.percentile(flat_residuals, 97.5)
            - np.percentile(flat_residuals, 2.5)
        ) / 2,
        'flat_rmse': math.sqrt(
            np.sum(flat_residuals**2) / len(flat_residuals)
        ),
        'slope_mean': np.mean(slope_residuals),
        'slope_rmse': math.sqrt(
            np.sum(slope_residuals ** 2) / len(slope_residuals)
        ),
        'slope_median': np.median(slope_residuals),
        'slope_std': np.std(slope_residuals),
        'slope_95p': (
            np.percentile(slope_residuals, 97.5)
            - np.percentile(slope_residuals, 2.5)
        ) / 2,
        'errors': [],
        'Test_results': []
    }

    # -----------------------------------------------------------------
    # Errors suggestions - These need revisiting and formalizing
    # -----------------------------------------------------------------
    errors = False
    # if abs(results['flat_mean']) > config.MAX_FLAT_MEAN:
    #     errors = True
    #     results['errors'].append("Flat mean threshold exceeded")

    # if results['flat_std'] > config.V_ERROR_THRESH:
    #     errors = True
    #     results['errors'].append("Flat std threshold exceeded")

    # if results['slope_std'] > config.H_ERROR_THRESH:
    #     errors = True
    #     results['errors'].append("Slope std threshold exceeded")

    if (
        results['ov_rmsd'] > results['ov_length']
        and results['ov_rmsd'] > config.MAX_OV_RMSD
        and len(results['slope_residuals']) > config.SAMPLE_NUM_THRESHOLD
    ):
        errors = True
        results['errors'].append(
            "Offset vector RMSE is relatively large;"
        )
        results['errors'].append(
            "vector may be a bad approximation"
        )

    # elif results['ov_length'] > config.H_ERROR_THRESH:
    #     errors = True
    #     results['errors'].append("Offset vector length threshold exceeded")
    if (
        results['flat_rmse'] > v_rmse_thresh
        and len(results['flat_residuals']) > config.SAMPLE_NUM_THRESHOLD
    ):
        errors = True
        results['errors'].append('Flat RMSE threshold exceeded')

    if (
        results['slope_rmse'] > h_rmse_thresh
        and len(results['slope_residuals']) > config.SAMPLE_NUM_THRESHOLD
    ):
        errors = True
        results['errors'].append('Slope RMSE threshold exceeded')

    if not errors:
        results['errors'].append("Lidar passed all tests")

    return results


def output_results(results, save_info=None):
    """
    Output test results to command line, then save results if necessary.
    """
    decimal_places = 1
    print(
        f"\n{config.AnsiColors.yellow}Results:{config.AnsiColors.reset}"
        f"\n\nHorizontal offset vector: [{round(results['offset_vector'][0], decimal_places)}, "
        f"{round(results['offset_vector'][1], decimal_places)}]"
        f"\n\tVector Length: {round(results['ov_length'], decimal_places)} cm"
        f"\n\tVector RMSE: {round(results['ov_rmsd'], decimal_places)} cm"

        f"\n\nFlat region stats:"
        f"\n\tSamples: {len(results['flat_residuals'])}"
        f"\n\tRMSD: {round(results['flat_rmse'], decimal_places)} cm"
        f"\n\tMean: {round(results['flat_mean'], decimal_places)} cm"
        f"\n\tMedian: {round(results['flat_median'], decimal_places)} cm"
        f"\n\tStd: {round(results['flat_std'], decimal_places)} cm"
        f"\n\t95th Percentile Deviation: {round(results['flat_95p'], decimal_places)} cm"

        f"\n\nSloped region stats:"
        f"\n\tSamples: {len(results['slope_residuals'])}"
        f"\n\tRMSD: {round(results['slope_rmse'], decimal_places)} cm"
        f"\n\tMean: {round(results['slope_mean'], decimal_places)} cm"
        f"\n\tMedian: {round(results['slope_median'], decimal_places)} cm"
        f"\n\tStd: {round(results['slope_std'], decimal_places)} cm"
        f"\n\t95th Percentile Deviation: {round(results['slope_95p'], decimal_places)} cm"
    )

    # print("Test Results:")
    # for e in results['errors']:
    #     print(e)
    # print("\nTask finished\n")

    if save_info is not None:
        save_results(results, save_info)
    else:  # Only output results to command line
        plt.hist(
            results['flat_residuals'],
            bins='fd',
            density=True,
            color='g',
            alpha=0.6
        )
        plt.xlabel("Residual Length (cm)")
        plt.ylabel("Frequency")
        plt.title("Histogram of Residuals in Flat Regions")
        plt.show()
        plt.hist(
            results['slope_residuals'],
            bins='fd',
            density=True,
            color='g',
            alpha=0.6
        )
        plt.xlabel("Residual Length (cm)")
        plt.ylabel("Frequency")
        plt.title("Histogram of Residuals in Sloped Regions")
        plt.show()


def print_friendly_time(datetime_time_obj):
    print_friendly_time = datetime_time_obj.strftime(
        "%Y-%m-%d, %H:%M:%S"
    )
    return print_friendly_time


def save_results(results, save_info):
    """
    Save the results into a csv and pdf.
    """
    outdir, start_time, fp1, fp2, company_name, v_rmse_thresh, h_rmse_thresh = save_info

    start_time_str = print_friendly_time(start_time)

    fn1 = fp1.name
    fn2 = fp2.name

    # -----------------------------------------------------------------
    #                           Results CSV
    # -----------------------------------------------------------------
    if len(results['flat_residuals']) < config.SAMPLE_NUM_THRESHOLD:
        results['flat_rmse'] = '--'
        results['flat_mean'] = '--'
        results['flat_std'] = '--'
        results['flat_95p'] = '--'

    if len(results['slope_residuals']) < config.SAMPLE_NUM_THRESHOLD:
        results['slope_rmse'] = '--'
        results['slope_mean'] = '--'
        results['slope_std'] = '--'
        results['slope_95p'] = '--'
        results['offset_vector'] = (0, 0)
        results['ov_length'] = 0
        results['ov_rmsd'] = 0

    # Key of dictionary used as header row; values used for row values
    results_row_values_dict = {
        "swaths": f"{fn1.split('.')[0]} {fn2.split('.')[0]}",
        "flat samples": len(results['flat_residuals']),
        "flat rmsd": results['flat_rmse'],
        "flat mean": results['flat_mean'],
        "flat std": results['flat_std'],
        "flat 95p": results['flat_95p'],
        "slope samples": len(results['slope_residuals']),
        "slope rmse": results['slope_rmse'],
        "slope mean": results['slope_mean'],
        "slope std": results['slope_std'],
        "slope 95p": results['slope_95p'],
        "offset vector": f"[{results['offset_vector'][0]} {results['offset_vector'][1]}]",
        "vector length": results['ov_length'],
        "vector rmsd": results['ov_rmsd']
    }

    # Populate list of row values from the dictionary
    results_row_values_list = []
    for item in results_row_values_dict:
        results_row_values_list.append(
            results_row_values_dict.get(item)
        )

    # Create the csv file and write the header row
    csv_fp = os.path.join(outdir, "lical_results.csv")

    if not os.path.exists(csv_fp):
        with open(csv_fp, 'a', newline='') as outfile:
            writer = csv.writer(outfile)

            # Write header rows with keys from row_values dict
            writer.writerow(
                list(results_row_values_dict)
            )

    # Write a row of results values to the csv file
    with open(csv_fp, 'a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(results_row_values_list)

    # Create folder to store temporary pdfs and png files
    # used to make the final report pdf.
    temp_dir = _temp_dir(outdir)

    # -----------------------------------------------------------------
    #                 Report PDF Begins - Title Information
    # -----------------------------------------------------------------
    report_location = os.path.join(
        temp_dir,
        f"Lical Report - {fn1.split('.')[0]}__{fn2.split('.')[0]}.pdf"
    )
    report = canvas.Canvas(
        report_location,
        # pagesize=letter
    )

    report.setFont(_bold_font(), 24)
    report.drawCentredString(300, 775, "LiCal QC Output Report")

    report.setFont(_regular_font(), 12)
    report.drawCentredString(300, 750, start_time_str)

    report.drawCentredString(300, 735, f"Company: {company_name}")

    report.drawCentredString(300, 710, f"Swath 1: {fn1}")
    report.drawCentredString(300, 695, f"Swath 2: {fn2}")

    # -----------------------------------------------------------------
    #                            Flat Results
    # -----------------------------------------------------------------
    plt.clf()
    if len(results['flat_residuals']) > config.SAMPLE_NUM_THRESHOLD:
        plt.hist(
            results['flat_residuals'],
            bins='fd',
            density=True,
            color='g',
            alpha=0.6
        )
        plt.xlabel("Residual Length (cm)")
        plt.ylabel("Frequency")
        plt.title("Histogram of Normal Magnitudes in Flat Regions")

        flat_hist_png_path = os.path.join(
            temp_dir,
            _flat_hist_png()
        )

        plt.savefig(flat_hist_png_path)

        flat_hist_img = Image(
            flat_hist_png_path,
            width=280,
            height=210
        )

        flat_hist_img.drawOn(report, 30, 480)

        report.setFont(_bold_font(), 12)
        report.drawCentredString(
            150,
            440,
            "Flat Normal Magnitude Statistics:"
        )

        report.setFont(_regular_font(), 12)

        report.drawString(
            100,
            420,
            f"Sample Size: {len(results['flat_residuals'])}"
        )

        report.drawString(
            100,
            405,
            f"RMSD: {round(results['flat_rmse'], 3)} cm"
        )

        report.drawString(
            100,
            390,
            f"Mean: {round(results['flat_mean'], 3)} cm"
        )

        report.drawString(
            100,
            375,
            f"Median: {round(results['flat_median'], 3)} cm"
        )

        report.drawString(
            100,
            360,
            f"Std: {round(results['flat_std'], 3)} cm"
        )

        report.drawString(
            100,
            345,
            f"P   : {round(results['flat_95p'], 3)} cm"  # extra space to accommodate subscript
        )

        report.setFont(_bold_font(), 6)

        report.drawString(106, 344, "95%")

        plt.clf()
    else:
        report.setFont(_regular_font(), 12)
        report.drawCentredString(
            150,
            600,
            "Insufficient flat samples for valid results"
        )
    # -----------------------------------------------------------------
    #                          Slope Results
    # -----------------------------------------------------------------
    if len(results['slope_residuals']) > config.SAMPLE_NUM_THRESHOLD:
        plt.hist(
            results['slope_residuals'],
            bins='fd',
            density=True,
            color='g',
            alpha=0.6
        )
        plt.xlabel("Residual Length (cm)")
        plt.ylabel("Frequency")
        plt.title("Histogram of Normal Magnitudes in Sloped Regions")

        slope_hist_png_path = os.path.join(
            temp_dir,
            _slope_hist_png()
        )

        plt.savefig(slope_hist_png_path)

        slope_hist_img = Image(
            slope_hist_png_path,
            width=280,
            height=210
        )

        slope_hist_img.drawOn(report, 300, 480)

        report.setFont(_bold_font(), 12)

        report.drawCentredString(
            450,
            440,
            "Sloped Normal Magnitude Statistics:"
        )

        report.setFont(_regular_font(), 12)

        report.drawString(
            400,
            420,
            f"Sample Size: {len(results['slope_residuals'])}"
        )

        report.drawString(
            400,
            405,
            f"RMSD: {round(results['slope_rmse'], 3)} cm"
        )
        report.drawString(
            400,
            390,
            f"Mean: {round(results['slope_mean'], 3)} cm"
        )
        report.drawString(
            400,
            375,
            f"Median: {round(results['slope_median'], 3)} cm"
        )

        report.drawString(
            400,
            360,
            f"Std: {round(results['slope_std'], 3)} cm"
        )
        report.drawString(
            400,
            345,
            f"P   : {round(results['slope_95p'], 3)} cm" # extra space to accommodate subscript
        )
        report.setFont(_bold_font(), 6)
        report.drawString(406, 344, "95%")

        plt.clf()
    else:
        report.setFont(_regular_font(), 12)
        report.drawCentredString(
            450,
            600,
            "Insufficient slope samples for valid results"
        )

    # -----------------------------------------------------------------
    #                    Chi-Square Results
    # -----------------------------------------------------------------
    report.setFont(_bold_font(), 12)
    report.drawCentredString(
        150,
        320,
        "Chi-Square Results:"
    )

    report.setFont(_regular_font(), 12)
    report.drawString(
        75,
        300,
        f"Test Statistic: {results['chi-square'][0]}"
    )
    report.drawString(
        75,
        285,
        f"Degrees of Freedom: {results['chi-square'][1]}"
    )
    report.drawString(
        75,
        270,
        f"Max: {results['chi-square'][2]}"
    )
    report.drawString(
        75,
        255,
        f"Min: {results['chi-square'][3]}"
    )
    report.drawString(
        75,
        240,
        f"Range: {results['chi-square'][4]}"
    )
    report.drawString(
        75,
        225,
        f"PValue: {results['chi-square'][5]}"
    )

    pvalue = results['chi-square'][5]
    percents = [0.01, 0.05, 0.1, 0.2]
    y = 210
    for i in percents:
        intPercent = int(i * 100)
        if pvalue > i:
            report.drawString(
                75,
                y,
                f"Accept {intPercent}%?:  Yes"
            )
        else:
            report.drawString(
                75,
                y,
                f"Accept {intPercent}%?:  No"
            )
        y -= 15

    # -----------------------------------------------------------------
    #                          Test Results
    # -----------------------------------------------------------------
    report.setFont(_bold_font(), 12)
    report.drawCentredString(
        450,
        320,
        "Test Results:"
    )

    report.setFont(_regular_font(), 12)
    for count, e in enumerate(results['errors']):
        report.drawCentredString(450, 300 - (count * 15), e)

    report.setFont(_regular_font(), 10)
    report.drawCentredString(
        300,
        95,
        f"Error Thresholds:    "
        f"vertical={v_rmse_thresh} cm    "
        f"horizontal={h_rmse_thresh} cm"
    )

    '''
    # -----------------------------------------------------------------
    #                    Horizontal Error Results
    # -----------------------------------------------------------------
    report.setFont(_bold_font(), 12)
    report.drawCentredString(300,320, f"[BETA] Horizontal Error Approximation:")

    report.setFont(_regular_font(), 12)
    report.drawString(220, 300,
        f"Offset Vector:  {np.round(results['offset_vector'], 3)}")
    report.drawString(220, 285,
        f"Vector Length:  {round(results['ov_length'], 3)} cm")
    report.drawString(220, 270,
        f"Vector RMSE:  {round(results['ov_rmsd'], 3)} cm")

    # -----------------------------------------------------------------
    #                          Test Results
    # -----------------------------------------------------------------
    report.setFont(bold_font, 12)
    report.drawCentredString(300, 230, "Test Results:")

    report.setFont(_regular_font(), 12)
    for count, e in enumerate(results['errors']):
        report.drawCentredString(300, 210 - (count * 15), e)

    report.setFont(_regular_font(), 10)
    report.drawCentredString(300, 95,
        f"Error Thresholds:    "
        f"vertical={v_rmse_thresh} cm    "
        f"horizontal={h_rmse_thresh} cm"
    )
    '''

    # -----------------------------------------------------------------
    #                       Report Disclaimer
    # -----------------------------------------------------------------
    report.setFont(_regular_font(), 8)
    report.drawCentredString(
        300,
        80,
        "This report is to be submitted to GeoBC without any alterations."
        "This software is intended to support, not replace, "
    )
    report.drawCentredString(
        300,
        70,
        "existing contractor quality control methods."
        "Thorough manual checks are still expected for final products."
    )

    report.drawCentredString(
        300,
        55,
        "Passing all the tests run by LiCal does not guarantee that a pair "
        "of lidar swaths are of high quality."
    )
    report.drawCentredString(
        300,
        45,
        "Conversely, failing these same tests does not necessarily mean the "
        "input lidar swaths contain systematic errors."
    )

    # -----------------------------------------------------------------
    #                         GeoBC Logo(s)
    # -----------------------------------------------------------------
    logo_data = base64.b64decode(config.GEOBC_LOGO_B64)
    logo_path = os.path.join(temp_dir, _geobc_logo_png())

    with open(logo_path, 'wb') as logo_file:
        logo_file.write(logo_data)

    logo_img = Image(logo_path, width=83, height=25)
    logo_img.drawOn(report, 25, 770)

    # -----------------------------------------------------------------
    #                           Watermark
    # -----------------------------------------------------------------
    # report.setFillColor(Color(0, 0, 1, alpha=0.075))
    # report.setFont(bold_font, 16)
    # for i in range(0,1):
    #     for j in range(0,11):
    #         pass
    #         report.drawString(5 + (j * 75), 20 + (i * 815), "GeoBC")
    report.save()

    # Add individual report results to full report.
    append_to_full_report(
        outdir,
        company_name,
        report_location
    )


def append_to_full_report(
    outdir,
    company_name,
    individual_report_path
):
    """
    Add individual report to the final merged report.
    """
    merger = PdfFileMerger()

    full_report_path = _full_report_path(outdir, company_name)

    if os.path.isfile(full_report_path):
        merger.append(
            PdfFileReader(full_report_path),
            "rb"
        )

    merger.append(individual_report_path)

    merger.write(full_report_path)
    merger.close()


def _temp_dir(outdir):
    temp_dir = os.path.join(
        outdir,
        "temp_lical_processing"
    )
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def _flat_hist_png():
    flat_hist_png = "flat_hist.png"
    return flat_hist_png


def _slope_hist_png():
    slope_hist_png = "slope_hist.png"
    return slope_hist_png


def _geobc_logo_png():
    geobc_logo_png = "geobc_logo.png"
    return geobc_logo_png


def _temp_png_list():
    temp_png_list = [
        _flat_hist_png(),
        _slope_hist_png(),
        _geobc_logo_png()
    ]
    return temp_png_list


def _regular_font():
    regular_font = "Helvetica"
    return regular_font


def _bold_font():
    bold_font = "Helvetica-Bold"
    return bold_font


def _full_report_path(outdir, company_name):
    full_report_path = os.path.join(
        outdir,
        f"LiCal_Report_{company_name}.pdf"
    )
    return full_report_path


def make_chi_table(
    chisquareResults,
    company_name,
    outdir
):
    for pair_result in chisquareResults:
        pair_result[1] = round(pair_result[1], 4)
        pair_result[3] = round(pair_result[1], 4)
        pair_result[4] = round(pair_result[1], 4)
        pair_result[5] = round(pair_result[1], 4)
        if pair_result[6] > 0.01:
            pair_result.append('Accept')
        else:
            pair_result.append('Reject')
        if pair_result[6] > 0.05:
            pair_result.append('Accept')
        else:
            pair_result.append('Reject')
        if pair_result[6] > 0.1:
            pair_result.append('Accept')
        else:
            pair_result.append('Reject')
        if pair_result[6] > 0.2:
            pair_result.append('Accept')
        else:
            pair_result.append('Reject')
    chisquareResults.insert(
        0,
        [
            'Swaths',
            'Chi-Square Sum',
            'Degrees of Freedom',
            'Max',
            'Min',
            'Range',
            'PValue',
            '1%',
            '5%',
            '10%',
            '20%'
        ]
    )
    chi_report_path = os.path.join(
        _temp_dir(outdir),
        "Chi-Square Test Results.pdf"
    )
    report = canvas.Canvas(
        chi_report_path,
        # pagesize=letter
    )
    doc = BaseDocTemplate(chi_report_path)
    width, height = letter

    left_header_frame = Frame(
        1.2 * inch,
        height - 0.5 * inch,
        2 * inch,
        1 * inch
    )

    right_header_frame = Frame(
        1.2 * inch,
        height - 0.5 * inch,
        width - 2.5 * inch,
        1 * inch, id='normal'
    )

    frame_later = Frame(
        0.2 * inch,
        0.6 * inch,
        width - 0.55 * inch,
        height - 0.5 * inch,
        leftPadding=0,
        topPadding=0,
        id='col'
    )

    frame_table = Frame(
        0.2 * inch,
        0.7 * inch,
        width - 0.55 * inch,
        height - 1 * inch,
        leftPadding=0,
        topPadding=0,
        id='col'
    )

    laterpages = PageTemplate(id='laterpages', frames=[frame_later])

    firstpage = PageTemplate(
        id='firstpage',
        frames=[
            left_header_frame,
            right_header_frame,
            frame_table
        ]
    )
    contents = []
    contents.append(NextPageTemplate('firstpage'))
    styleSheet = getSampleStyleSheet()
    style_title = styleSheet['Heading1']
    style_title.fontSize = 24
    style_title.fontName = _bold_font()
    style_title.alignment = 1

    # report.setTitle('Chi-Square Test Results')

    contents.append(FrameBreak())
    contents.append(Paragraph('Chi-Square Test Results', style_title))
    contents.append(FrameBreak())

    report.setFont(_regular_font(), 6)

    t = Table(chisquareResults)
    t.setStyle(
        TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('SPAN', (0, 0), (0, 0))
            ]
        )
    )

    contents.append(NextPageTemplate('laterpages'))
    contents.append(t)
    contents.append(PageBreak())

    doc.addPageTemplates([firstpage, laterpages])
    doc.build(contents)

    append_to_full_report(
        outdir,
        company_name,
        chi_report_path
    )


def roll_data(data, offset=10):
    """Simulate a roll/pitch error into a data set."""
    x_mean = np.mean(data, axis=0)[0]
    x_max = np.max(data, axis=0)[0]
    # x_min = np.min(data, axis=0)[0]

    dist_from_center = x_mean - data[:, 0]
    z_offsets = (dist_from_center / (x_max - x_mean)) * offset
    data[:, 2] += z_offsets

    return data


def shift_data(data, index=2, offset=5):
    """Shift a dataset by a flat amount in one axis."""
    data[:, index] += offset

    return data


def print_friendly_duration(datetime_timedelta_duration):
    """
    Truncate a datetime.timedelta object to
    two decimal places (10-millisecond precision),
    return as a string.

    e.g., if input is 0:00:00.505213,
    the output is "0:00:00.50"
    """
    # Truncate string to first ten characters (two decimal places)
    print_friendly_duration = str(datetime_timedelta_duration)[:10]

    return print_friendly_duration

class BoundingBox:
    """
    Describes a geometric rectangle by its bounding coordinates
    """
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def to_list(self):
        """Convert the bounding box to a 2d list format."""
        return [[self.xmin, self.xmax], [self.ymin, self.ymax]]


def parse_header(filename, verbose=False):
    """
    Parse a las/laz file's header into a workable struct format.
    """
    headerstruct = (
        ('filesig', 4, 'c', 4),
        ('filesourceid', 2, 'H', 1),
        ('reserved', 2, 'H', 1),
        ('guid1', 4, 'L', 1),
        ('guid2', 2, 'H', 1),
        ('guid3', 2, 'H', 1),
        ('guid4', 8, 'B', 8),
        ('vermajor', 1, 'B', 1),
        ('verminor', 1, 'B', 1),
        ('sysid', 32, 'c', 32),
        ('gensoftware', 32, 'c', 32),
        ('fileday', 2, 'H', 1),
        ('fileyear', 2, 'H', 1),
        ('headersize', 2, 'H', 1),
        ('offset', 4, 'L', 1),
        ('numvlrecords', 4, 'L', 1),
        ('pointformat', 1, 'B', 1),
        ('pointreclen', 2, 'H', 1),
        ('numptrecords', 4, 'L', 1),
        ('numptbyreturn', 20, 'L', 5),
        ('xscale', 8, 'd', 1),
        ('yscale', 8, 'd', 1),
        ('zscale', 8, 'd', 1),
        ('xoffset', 8, 'd', 1),
        ('yoffset', 8, 'd', 1),
        ('zoffset', 8, 'd', 1),
        ('xmax', 8, 'd', 1),
        ('xmin', 8, 'd', 1),
        ('ymax', 8, 'd', 1),
        ('ymin', 8, 'd', 1),
        ('zmax', 8, 'd', 1),
        ('zmin', 8, 'd', 1),
        ('waveform', 8, 'Q', 1),
        ('firstEVLR', 8, 'Q', 1),
        ('numEVLR', 4, 'L', 1),
        ('exnumbptrec', 8, 'Q', 1),
        ('exnumbyreturn', 120, 'Q', 15)
    )

    header = {'infile': filename}

    with open(filename, 'rb') as fh:
        for i in headerstruct:
            if i[2] == 'c':
                value = fh.read(i[1])
            elif i[3] > 1:
                value = struct.unpack(f"={str(i[3])}{i[2]}", fh.read(i[1]))
            else:
                value = struct.unpack(f"={i[2]}", fh.read(i[1]))[0]
            if verbose:
                print(f"{i[0]}\t", f"{i[2]}\t", value)

            header[i[0]] = value

    # if laz file, subtract 128 from the point data format
    # (laz compression adds 128 to the point format)
    if header['infile'].suffix == '.laz':
        header['pointformat'] = header['pointformat'] - 128

    return header


def _delete_temp_png_files(outdir):
    """
    Delete the temporary .png files used to
    add images to the .pdf report
    """
    temp_png_list = _temp_png_list()
    temp_dir = _temp_dir(outdir)
    for png_file in temp_png_list:
        png_path = os.path.join(temp_dir, png_file)
        if os.path.exists(png_path):
            os.remove(png_path)


def _delete_temp_dir(outdir):
    """
    Delete the temporary directory containing the
    the component pdfs and any remaining pngs
    used to create the final report.
    """
    temp_dir = _temp_dir(outdir)
    shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()
