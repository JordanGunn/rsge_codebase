import os
from osgeo import gdal

def run_from_gui(fList, outdir, recurse):
    # this allows GDAL to throw Python Exceptions
    gdal.UseExceptions()

    # Script will recursively go through subdirectories and report information about each tif image. If there is
    # a corrupt image it will add an entry to a csv. place script in parent folder and run.

    # Tk().withdraw()
    # Specify input and output directory
    # indir = filedialog.askdirectory(title='Select input directory')

    tif_list = []
    jpg_list = []
    sid_list = []
    for file in fList:
        if os.path.splitext(file) == ".tif" or ".tiff":
            tif_list.append(file)
        elif os.path.splitext(file) == ".jpg" or ".jpeg":
            jpg_list.append(file)
        elif os.path.splitext(file) == ".sid":
            sid_list.append(file)

    tif_errors = checkTif(tif_list)
    jpg_errors = checkJpg(jpg_list)
    sid_errors = checkSid(sid_list)
    
    totalFiles = len(tif_list) + len(jpg_list) + len(sid_list)

    output(outdir, totalFiles, tif_errors, jpg_errors, sid_errors, recurse)

def checkTif(tif_list):  
    tif_errors = []
    for idx,image in enumerate(tif_list, start=1):

        #print("\r Checking tif file {} of {}".format(idx, len(tif_list)), end='')

        image = str(image)
        try:
            tif = gdal.Open(image)
            statinfo = os.stat(image)
            size = statinfo.st_size / 1e6
            cols = tif.RasterXSize
            rows = tif.RasterYSize

            tif = None

        except RuntimeError as e:
            x = image, e
            tif_errors.append(x)
           
    return tif_errors

def checkJpg(jpg_list):  
    jpg_errors = []
    for idx,image in enumerate(jpg_list, start=1):

        #print("\r Checking jpg/jpeg file {} of {}".format(idx, len(jpg_list)), end='')

        image = str(image)
        try:
            jpg = gdal.Open(image)
            statinfo = os.stat(image)
            size = statinfo.st_size / 1e6
            cols = jpg.RasterXSize
            rows = jpg.RasterYSize

            jpg = None

        except RuntimeError as e:
            x = image, e
            jpg_errors.append(x)
           
    return jpg_errors

def checkSid(sid_list):  
    sid_errors = []
    for idx,image in enumerate(sid_list, start=1):

        #print("\r Checking sid file {} of {}".format(idx, len(sid_list)), end='')

        image = str(image)
        try:
            sid = gdal.Open(image)
            statinfo = os.stat(image)
            size = statinfo.st_size / 1e6
            cols = sid.RasterXSize
            rows = sid.RasterYSize

            sid = None

        except RuntimeError as e:
            x = image, e
            sid_errors.append(x)
           
    return sid_errors

def output(outdir, totalFiles, tif_errors, jpg_errors, sid_errors, recurse):
    
    tif_error_len = len(tif_errors)
    jpg_error_len = len(jpg_errors)
    sid_error_len = len(sid_errors)

    totalErrors = tif_error_len + jpg_error_len + sid_error_len

    with open(f'{outdir}\\corrupted_files.txt', mode='w+') as out:
        print(f"Corrupt files: {totalErrors} of {totalFiles}", file=out)
        print(f"\nList of corrupt files:", file=out)
        x = 0
        if tif_error_len > 0:
            for x in range(tif_error_len):
                print(tif_errors[x], file=out)
            x = 0
        if jpg_error_len > 0:    
            for x in range(jpg_error_len):
                print(jpg_errors[x], file=out)
            x = 0
        if sid_error_len > 0:
            for x in range(sid_error_len):
                print(sid_errors[x], file=out)
    '''
    with open(os.path.join(outdir, 'image_errors.csv', 'a+')) as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerow('Corrupt files: ', totalErrors, ' of ' totalFiles)
        if tif_error_len > 0:
            for x in tif_error_len:
                wr.writerow(tif_errors[x])
            x = 0
        if jpg_error_len > 0:    
            for x in jpg_error_len:
                wr.writerow(jpg_errors[x])
            x = 0
        if sid_error_len > 0:
            for x in sid_error_len:
                wr.writerow(sid_errors[x])
    '''
    if (tif_error_len or jpg_error_len or sid_error_len) > 0:
            print('!!!!!!!!!!!!!!! Corrupt images found !!!!!!!!!!!!!!!!!\n')
    else:
        print('No corrupt image files')

    #print('\n\nPress enter to close')
    #input()