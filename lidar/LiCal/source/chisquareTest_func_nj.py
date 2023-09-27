# This script is a sandbox to work on fixing the chi2 test.
#
# NJ working on fixing chi2 test -- edited variables for finding number of bins and bin widths
# copied current version of lical into separate file to begin testing with sample data
# does Sturge's rule work appropriately for the number of samples? NO! read on!
# print number of samples too for more info.............

import datetime
import random
import base64
import math
import time
import csv
import sys
import os

import warnings
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, BaseDocTemplate, Table, TableStyle, NextPageTemplate, \
PageTemplate, Paragraph, Frame, FrameBreak, PageBreak
from reportlab.lib import colors
#from PyPDF2 import PdfFileMerger, PdfFileReader
import scipy.stats as stats
from scipy import spatial

import numpy as np
import laspy
import tqdm

from shapely.geometry import Polygon
from matplotlib import path as mpltPath
from scipy.spatial import ConvexHull, cKDTree
from pathlib import Path

from itertools import combinations, chain
import struct

#import config

dashline = "-" * 80

# ------------------------------------------------------------------------------
# NJ flip this switch to use lidar residuals or a small boutique dataset
use_lidar_residuals, fromBrett = False, True


# Choose a binning method
# binningMethod = "Sturges"
# binningMethod = "Scott"
binningMethod = "Freedman and Diaconis"
# binningMethod, brute_force_bin_width = "brute force", 0.02

# Sample residuals from lidar data
if use_lidar_residuals:
    import pickle

    if fromBrett:
        path = r'C:\PYTHON\LICAL_STATS_TESTING\lical_testing_nj\test_input_data\bc_092h030_4_2_3_xyes_8_utm10_2019'
        filename = "bc_092h030_4_2_3_xyes_8_utm10_2019_20761__bc_092h030_4_2_3_xyes_8_utm10_2019_50813.pkl"
    else:
        path = r'C:\PYTHON\LICAL_STATS_TESTING\lical_testing_nj\test_input_data'
        filename = "flat_residuals.pkl" # there are some big outliers in this dataset; not very flat?
    fullpath = os.path.join(path, filename)
    f = open(fullpath, 'rb')
    data = pickle.load(f)

    test_results = {'all_residuals': data}

# Alternatively, use this small dataset:
else:
    filename = "just a little dataset, not from lidar"
    test_results = {'all_residuals' : [3.5465, 7.4567, 6.1423, -2.240, -3.3445, 7.8464, -4.4564, 10.4546, -12.3544]}
# ------------------------------------------------------------------------------


def chisquareTest(test_results):
    print(f"Dataset: {filename}")
    print(f"Binning method: {binningMethod}")
    values = test_results['all_residuals']
    values = np.array(values) # is this line necessary? values is already a np array -- except if using test data, so keep this line.
    numOfSamples = len(values)
    print(f"Number of samples: {numOfSamples}")
    mean = values.mean()
    stdev = values.std(ddof=1)
    print(f'Mean: {mean}')
    print(f'Stdev: {stdev}')
    valRange = max(values) - min(values)
    print(f'Value range: {valRange}')

    plt.plot()
    
    if binningMethod == "Sturges":
        # Optimal number of bins based on Sturge's rule:
        initBins = (1 + 3.3 * math.log10(numOfSamples))
        print(f"Optimal number of bins based on Sturge's rule: {initBins}")
        initWidth = valRange/initBins
        print(f"Initial width of bins before rounding: {initWidth}")
    elif binningMethod == "Scott":
        # Formula from: https://robjhyndman.com/papers/sturges.pdf
        initWidth = 3.5 * stdev * numOfSamples**(-1/3)
        print(f"Optimal bin width based on Scott's rule: {initWidth}")
    elif binningMethod == "Freedman and Diaconis":
        q1, q3 = np.percentile(values, [25, 75])
        interquaretilerange = q3 -  q1
        # Formula from: https://robjhyndman.com/papers/sturges.pdf
        initWidth = 2 * interquaretilerange * numOfSamples**(-1/3)
        print(f"Optimal bin width based on Freedman and Diaconis's rule: {initWidth}")
    elif binningMethod == "brute force":
        initWidth = brute_force_bin_width
        print(f"The brute force bin width is: {initWidth}")
    else:
        print("No binning method chosen! Aborting script!")
        sys.exit()

    numOfBins = math.ceil(valRange/initWidth) # round number of bins up to integer
    degreesOfFreedom = numOfBins - 1
    print(f"Number of bins used: {numOfBins}")
    binWidth = valRange/numOfBins
    print(f"Bin width: {binWidth}")

    bounds = []
    normalProbability=[]
    predictedFreq = []
    observedFreq = []
    chiSquare = []
    bounds.append(min(values))

    # For each bin,
    for i in tqdm.tqdm(range(numOfBins)):
        
        # Append the right bound of the bin to the list of bounds (this will be the bounds[i+1] value)
        bounds.append(round(bounds[i] + binWidth, 10)) # round to 10 decimal places
        
        # Calculate the area of the bin slice between bin bounds for a normal distribution
        normalProbability.append(stats.norm.cdf(bounds[i+1], mean, stdev)-stats.norm.cdf(bounds[i], mean, stdev))
        
        # Scale the area of the normal distribution slice to match the scale of the samples
        predictedFreq.append(normalProbability[i] * numOfSamples)

        # If in the last bin, include values on the right bound in that bin
        if i == numOfBins-1:
            observedFreq.append(sum(num >= bounds[i] and num <= bounds[i+1] for num in values))
        
        # For all other bins, don't include values that fall on the right bound in that bin
        else:
            observedFreq.append(sum(num >= bounds[i] and num < bounds[i+1] for num in values))
        
        # Do we need an if-clause for cases where the normal distribution is zero? (optional? maybe recommended to not crash program if no data?)
        #if predictedFreq[i] != 0:

        # Calculate the chi-square addend for the given bin
        chiSquare.append((predictedFreq[i]-observedFreq[i])**2/predictedFreq[i])

    # Sum all the chi-square addends from each bin to get the chi-square statistic
    chiSum = sum(chiSquare)
    print(f"chi2Value (chiSum): {chiSum}")

    # Calculate the p-value for the given chi-square value and degrees of freedom
    pValue = stats.chi2.sf(chiSum, numOfBins-1) # original line


    observedFreqSum = sum(observedFreq)
    predictedFreqSum = sum(predictedFreq)
    print(f"{dashline}\nObserved freq sum: {observedFreqSum}\nPredicted freq sum: {predictedFreqSum}\n{dashline}\n")
    print(f"Values: {np.sort(values)}")
    print(f"Bounds: {bounds}")
    print(f"Observed frequencies per bin ({len(observedFreq)}): {observedFreq}\nPredicted frequencies per bin (normal distribution) ({len(predictedFreq)}): {predictedFreq}")
    #new_method = stats.chisquare(f_obs=observedFreq, f_exp=predictedFreq)
    #print(f"New method: {new_method}")

    #plt.hist(values, bins=numOfBins)
    #plt.show()

    #plt.hist(values, cumulative=True, label="CDF")
    #plt.show()
    
    return [
        chiSum,  # 0
        numOfBins-1,  # 1
        max(values),  # 2
        min(values),  # 3
        valRange,  # 4
        pValue,  # 5
        values,  # 6
        mean,  # 7
        stdev  # 8
    ]    # returning "values", mean, and stdev variable only for plotting purposes outside function

#-------------------------------------------------------------------------------
# EXECUTE FUNCTION AND DISPLAY RESULTS

print(dashline)

chisquareresult = chisquareTest(test_results)

print(f"Max residual: {chisquareresult[2]}\n"
    f"Min residual: {chisquareresult[3]}\n"
    f"P-value: {chisquareresult[5]}\n"
    f"{dashline}"
)
critical_value95 = stats.chi2.ppf(q=0.95, df=chisquareresult[1])
print(f"Critical value for 95% CL: {critical_value95}")

plt.hist(chisquareresult[6], bins=(chisquareresult[1] + 1), color="blue")
plt.plot(chisquareresult[6], stats.norm.pdf(chisquareresult[6], chisquareresult[7], chisquareresult[7]), color="red")
plt.title("Histogram")
plt.xlabel("Data values")
plt.ylabel("Frequency")
plt.show()


#------------------------------------------------------------------------------- 
