import subprocess
from osgeo import gdal
import os
import concurrent.futures
import glob

from tkinter.filedialog import askdirectory
from tkinter import Tk

# from tqdm import tqdm

class CloudOptimizedGeotiff:

    '''
    Class to create cloud optimized geotiffs

    - Input: ESRI ASCII, USGS DEM, Geotiff
    - Output: Cloud Optimized Geotiff (COG)
    - Applies deflate compression
    - Applies internal tiling of blocksize 512
    - Applies internal overviews
    - Re-organizes file structure to match valid cloud optimized geotiff standards
    '''

    def __init__(self):
        
        # define creation option values
        self.predictor = 3 
        self.epsg = None
        self.compress_method = 'DEFLATE'  # [OTHER OPTIONS: 'LZW', 'ZSTD', 'PACKBITS', 'LERC_DEFLATE']
        self.compress_level = 6  
        self.overview_levels = 2, 4
        self.resampling = 'cubic'
        self.blockxsize = 512
        self.blockysize = 512
        self.lerc_threshold = .01
        self.jpeg_quality = 75
        
        # create dictionary to assign projection from filename (All projections wrt to NAD83 (CSRS))
        self.proj_dict = {
            'utm08': 3155, 
            'utm8': 3155,
            'utm09': 3156,
            'utm9': 3156,
            'utm10': 3157,
            'utm11': 2955,
            'bcalb': 3005
            }

        # append to gdal command if compression method is LERC !!! added in anticipation of potentially using LERC (Limited Error Raster Compression) !!!
        if self.compress_method == 'LERC_DEFLATE':
            self.compress_method += f' -co MAX_Z_ERROR={self.lerc_threshold}'

        # append to gdal command is compression method is JPEG
        if self.compress_method == 'JPEG':
            self.compress_method += f' -co JPEG_QUALITY={self.jpeg_quality}'

        # set global GDAL configuration options
        gdal.SetConfigOption('GDAL_TIFF_OVR_BLOCKSIZE', f'{self.blockxsize}')
        gdal.SetConfigOption('COMPRESS_OVERVIEW', f'{self.compress_method}')
        gdal.UseExceptions()  # Allow gdal to make use of python exceptions for error handling

    

    """Method to batch convert USGS DEM, ESRI ASCII and Geotiff format DEMs to compressed and internally tiled Geotiffs"""
    def compress_and_tile(self, args):
        file, out_dir = args
        
        # change directory to output location
        os.chdir(out_dir)
        
        # loop through files and convert, compress, and internally tile new tif files
        #print('Compressing and creating internal tiling...')
        # try to get projection from filename, if no projection in the filename, filename is wrong. 
        try:
            str_str = os.path.splitext(os.path.basename(file))[0].split('_')  # split filename by underscore
            for ind, s in enumerate(str_str):
                if 'utm' in s or 'bcalb' in s: # check for proj in filename
                    proj = str_str[ind]  # use index value to get proj from split string np.array
                    self.epsg = self.proj_dict[proj]  # use index value as key to get value from dictionary
                    prj = True
                    break
                else:
                    prj = False
        except:
            wrong_fname = open(os.path.join(out_dir, 'wrong_filename.txt'), 'a+')  # create file to log incorrectly named files
            wrong_fname.write(os.path.basename(file) + '\n')  # write the filename to the text file
            wrong_fname.close()  # close the file

        # Create gdal_translate command options
        if prj:
            trans_str = f'-of GTiff -a_srs EPSG:{str(self.epsg)} -co PREDICTOR={str(self.predictor)} -q -co TILED=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS={self.compress_method} -co ZLEVEL={str(self.compress_level)}'
        elif not prj:
            trans_str = f'-of GTiff -co PREDICTOR={str(self.predictor)} -q -co TILED=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS={self.compress_method} -co ZLEVEL={str(self.compress_level)}'
        if self.compress_method == 'JPEG':
            trans_str = f'-of GTiff -a_srs EPSG:{str(self.epsg)} -q -co TILED=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS={self.compress_method}'
        
        # parse command line syntax to be passed to translate options
        tp = gdal.ParseCommandLine(trans_str)
        # pass parsed string to TranslateOptions object
        trans_opt = gdal.TranslateOptions(tp)
        
        # define output name
        out_name = f'{os.path.splitext(os.path.basename(file))[0]}.tif'
        # if file already exists, pass (in case of failed or interrupted processing, you can pick back up where you left off)
        if os.path.exists(out_name):
            pass
        else:
            try:
                gdal.Translate(out_name, file, options=trans_opt)  # pass translate options to gdal.Translate()
            except Exception as e:
                err = open(os.path.join(out_dir, 'compression_and_tiling_errors.txt'), 'a+')
                err.write(f'{file}\t{e}\n')
                err.close()

    """Method to create overviews using GDAL's python api"""
    def batch_create_overviews_py(self, list_of_files):
        # append path to osgeo4w and GDAL to environment variables
        os.environ["PATH"] += os.pathsep + r'C:\OSGeo4W64\bin'
        os.environ["PATH"] += os.pathsep + r'C:\Program Files\GDAL'
        # loop through files, create overviews
        #print('Adding overviews...')
        for f in list_of_files:
            im = gdal.Open(f)  # Create gdal datasource object
            im.BuildOverviews('CUBIC', [2, 4])  # build overviews; resampling=CUBIC, overview levels equals 2 (half) and 4 (quarter)
            im = None

    """Method to create overviews using gdal's typical command line call through subprocess"""        
    def batch_create_overviews(self, in_dir):
        # append path to osgeo4w and GDAL to environment variables
        os.environ["PATH"] += os.pathsep + r'C:\OSGeo4W64\bin'
        os.environ["PATH"] += os.pathsep + r'C:\Program Files\GDAL'

        # clean overview levels string
        overview_levels_str = str(self.overview_levels).replace('(', '').replace(')', '').replace(',', '')
        
        # create command line string for gdaladdo utility
        #print('Creating overviews...')
        addo_str = f'FOR %F in (*.tif) DO gdaladdo -r {self.resampling} %F {overview_levels_str} '
        # call gdaladdo string to command prompt
        subprocess.call(addo_str, shell=True)

    """Method to create final Cloud Optimized Geotiff (COG)"""
    def batch_create_cog(self, file_list, odir):
        # create gdal_translate command string
        trans_str = f'-co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS={self.compress_method} -co NUM_THREADS=ALL_CPUS -co BLOCKXSIZE={str(self.blockxsize)} -co BLOCKYSIZE={str(self.blockysize)}'

        # parse command line syntax to be passed to translate options
        tp = gdal.ParseCommandLine(trans_str)

        # pass parsed string to TranslateOptions object
        trans_opt = gdal.TranslateOptions(tp)
        
        out = os.path.join(odir + '/COG')
        if not os.path.exists(out):
            os.mkdir(out)  # make the dir
            os.chdir(out)  # navigate to dir

        # loop through files and write the final COGS
        #print('\nCreating cloud optimized geotiffs...')
        for file in file_list:
            out_name = f'{os.path.splitext(os.path.basename(file))[0]}.tif'
            # if file already exists, pass
            if os.path.exists(out_name):
                pass
            else:
                try:
                    gdal.Translate(out_name, file, options=trans_opt)  # pass translate options to gdal.Translate()
                # if error encounters, write it to a text file
                except Exception as e:
                    err = open(os.path.join(out, 'COG_creation_errors.txt'), 'a+')
                    err.write(f'{file}\t{e}')
                    err.close()

    """Static method for removing intermediate tifs created during first gdal_translate process"""
    @staticmethod
    def remove_intermediate_tif(in_dir):
        # Remove intermediate files
        print('\nRemoving intermediate files...', flush=True)
        extensions= ("*.tif", "*.tiff")
        interTifs = []
        for extension in extensions:
            interTifs.extend(glob.glob(in_dir+"/"+extension))
        #interTifs = glob.glob(os.path.join(in_dir + '/*.tif'))

        for f in range(len(interTifs)):
            os.remove(interTifs[f])

    def gdalwarp_create_cog(self, args):
        file, outdir = args
        out_file = f"{outdir}\{os.path.basename(file)}"
        subprocess.call(f"C:\OSGeo4W\OSGeo4W.bat gdalwarp {file} {out_file} -co OVERVIEWS=IGNORE_EXISTING -of COG", stdout=open(os.devnull, 'wb'))

    def run_from_gui(self, flist, odir, cores):
        
        odir = os.path.join(odir + '/COG')
        if not os.path.exists(odir):
            os.mkdir(odir)

        with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
            [executor.submit(self.gdalwarp_create_cog, [file, odir]) for file in flist]
        
        
    '''def run_from_gui(self, flist, odir, compRatio, validateCOG, cores):6

        # change directory to output location
        os.chdir(odir)
        
        self.compress_level = compRatio
        #flist = []   
        # use wildcards to compile list
        #for e in ('*.asc', '*.dem', '*.tif'):
            #flist.extend(glob(os.path.join(idir, e), recursive=True))

        # report number of files to be converted 
        #print('\n' + str(len(flist)) + ' image files found\n')
        #print("odir: ", odir)
        
        # run the gdal.Translate function
        #print("before compress_and_tile", flush = True)
        with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
            [executor.submit(self.compress_and_tile, [file, odir]) for file in flist]
        #print("after compress_and_tile", flush = True)
        # generate overviews
        self.batch_create_overviews(odir)

        # use wildcards to collect new tifs
        extensions= ("*.tif", "*.tiff")
        tif_list = []
        for extension in extensions:
            tif_list.extend(glob.glob(odir+"/"+extension))
            
        # generate cogs
        #with concurrent.futures.ProcessPoolExecutor() as executor:
            #[executor.submit(self.batch_create_cog, [file, out]) for file in tif_list]
        self.batch_create_cog(tif_list, odir)
        # remove intermediate files
        self.remove_intermediate_tif(odir)
        
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=cores) as executor:
            [executor.submit(self.compress_and_tile, [file, odir]) for file in flist]

        if validateCOG is True:
            import Validate_COG
            COGPath = os.path.join(odir + '/COG')
            cogList = glob.glob(COGPath+"/*.tif")
            Validate_COG.run_from_gui(cogList, COGPath)

        '''
    
    """Method for running the script"""
    def runCMD(self):
        # Close empty tkinter window
        Tk().withdraw()

        # Specify input and output directory
        idir = askdirectory(title='Select input directory')
        odir = askdirectory(title='Select output directory')
        # request input for epsg code
        # self.epsg = input('Enter epsg code for output or type "None":\t')

        # change directory to output location
        os.chdir(odir)

        # create list of files
        extensions= ("*.tif", "*.tiff", "*.asc", "*.dem")
        flist = []
        for extension in extensions:
            flist.extend(glob.glob(idir+"/"+extension))
        #flist = []   
        # use wildcards to compile list
        #for e in ('*.asc', '*.dem', '*.tif'):
            #flist.extend(glob(os.path.join(idir, e), recursive=True))

        # report number of files to be converted 
        #print('\n' + str(len(flist)) + ' image files found\n')

        # run the gdal.Translate function
        self.compress_and_tile(flist, odir)
        # generate overviews
        self.batch_create_overviews(odir)

        # use wildcards to collect new tifs
        tifExtensions = ("*.tif", "*.tiff")
        tif_list=[]
        for tExtension in tifExtensions:
            flist.extend(glob.glob(idir+"/"+tExtension))
        #tif_list = glob.glob(os.path.join(odir + '/*tif'))
        #tif_list = glob(os.path.join(odir, e))
        
        # generate cogs
        self.batch_create_cog(tif_list, odir)
        # remove intermediate files
        self.remove_intermediate_tif(odir)

        print('Done!')
   

if __name__ == '__main__':
    # instantiate COG class
    cog = CloudOptimizedGeotiff()
    # call the run method
    cog.runCMD()
