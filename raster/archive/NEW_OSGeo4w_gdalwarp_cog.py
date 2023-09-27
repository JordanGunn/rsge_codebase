import subprocess
import os





if __name__=='__main__':
    import glob
    from tkinter import filedialog, Tk
    Tk().withdraw()

    # prompt for indir and outdir
    indir = filedialog.askdirectory(title="Select input tif directory")
    outdir = filedialog.askdirectory(title="Select output directory")

    files = glob.glob(os.path.join(indir, '*.tif'))

    print(f"Generating {len(files)} COGs")
    for f in files:
        out_file = f"{outdir}\{os.path.basename(f)}"
        subprocess.call(f"C:\OSGeo4W\OSGeo4W.bat gdalwarp {f} {out_file} -of COG", shell=True)
        

    print('Done!')
