# For when you have a big ol' folder full of lidar swaths and you
# want to run LiCal on all of them. If running this on lasdecompose
# results, make sure to seperate the swaths into a different folder
# from the original composite lidar file.
#
# This could run LiCal up to n^2 times, for n lidar files in indir,
# so beware, it might take a loooooong time to run.
#
# Written by Graeme Prendergast

import itertools
# import glob
import time
import sys
# import os
from pathlib import Path

import lical


def main():
    try:
        indir = Path(sys.argv[1])
    except Exception:
        print(
            "Argument formatting:"
            "\n>> python batch_lical.py <indir>"
        )
        return

    # lidar_glob = [f for f in glob.glob(f'{indir}\\*')
    #                   if f.split('.')[-1] in {'las','laz'}]
    las_files = indir.rglob('*.las')
    laz_files = indir.rglob('*.laz')
    lidar_glob = itertools.chain(las_files, laz_files)

    start_time = time.time()

    combinations = list(itertools.combinations(lidar_glob, 2))
    for count, pair in enumerate(combinations):
        print(f"Pair {count + 1} of {len(combinations)}:")
        try:
            lical.run_from_gui(pair[0], pair[1], indir, "GeoBC (batch_lical)")
        except Exception as e:
            print(e)
            continue

    print(f"\n\nBatch LiCal runtime: {time.time() - start_time} seconds")


if __name__ == '__main__':
    main()
