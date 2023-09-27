# Let's decompose some lidar!
# Written by Graeme Prendergast
# Updated for laspy >= 2.0 by Natalie Jackson

import time
import sys
import os

import numpy as np
import laspy


def decompose(infile_path, outdir, verbose=False):
    """
    Decompose a composite lidar file into its constituent swaths.

    The .las files this function creates are version 1.4, but I'm not
    sure whether or not this method of .las creation stomps on any of
    the metadata from the input file. Use with care!

    Args:
        infile_path : Absolute path to the input lidar file
        verbose : Optional keyword argument to print additional info
    Returns:
        None
    """
    decomposed_lidar_folder, filename_no_ext, ext = _prep_output_folder_and_filename(
        infile_path,
        outdir
    )

    if verbose:
        print(f"Reading/decompressing {filename_no_ext}{ext}...")

    # Make a laspy LasData object from the input file
    infile = laspy.read(
        infile_path,
        laz_backend=laspy.LazBackend.LazrsParallel
    )

    # Identify the unique swath ids within the input file
    source_ids = np.unique(infile.point_source_id)

    if verbose:
        print(f"Source ids: {source_ids}")

    # Iterate through each swath
    for index, id in enumerate(source_ids, start=1):
        # Create a new laspy LasData object with the same
        # point format and las version as the input file
        outfile = laspy.create(
            point_format=infile.header.point_format,
            file_version=infile.header.version
        )

        # Create a filter for the point source id
        # to identify points in a file that have
        # a specified point source id.
        # (i.e., they belong to to the same flight line/swath)
        # e.g., if the flight line id is 123 (id = 123),
        # and point source array of infile
        # looks like:
        #   infile.point_source_id = [123 999 999 123 123]
        # the filter will be:
        #   [True False False True True]
        point_source_filter = infile.point_source_id == id

        # Filter the points from the original points
        # and assign them to the new file
        outfile.points = infile.points[point_source_filter]

        # Define the output path and filename
        outfile_path = os.path.join(
            decomposed_lidar_folder,
            f"{filename_no_ext}_{id}.las"
        )

        if verbose:
            print(
                f"Writing flightline {id} for file {index} of {len(source_ids)}",
                "\r",
                end=""
            )

        # Write the new las file
        outfile.write(outfile_path)


def _prep_output_folder_and_filename(infile_path, outdir):
    """
    Create output folder if it does not exist,
    and extract the input file name to use
    in the output file names.
    """
    decomposed_lidar_folder = os.path.join(outdir, "decomposed_lidar")

    if not os.path.exists(decomposed_lidar_folder):
        os.makedirs(decomposed_lidar_folder)

    filename = os.path.basename(os.path.normpath(infile_path))

    filename_no_ext, ext = os.path.splitext(filename)

    return decomposed_lidar_folder, filename_no_ext, ext


if __name__ == '__main__':
    try:
        infile_path = sys.argv[1]
    except Exception:
        print(
            "Argument formatting:"
            "\n>> python lasdecompose.py <input-lidar>"
        )
        sys.exit()

    outfile_path = os.path.join(
        os.path.split(infile_path)[0],
        "decompose_outputs"
    )

    start_time = time.time()

    decompose(infile_path, outfile_path)

    print(
        f"\nRuntime: {time.time() - start_time} seconds"
    )
