'''
Written by Brett Edwards, GeoBC
Purpose: Provide an easy interface to compress imagery for archiving, generate thumbnails, and/or generate COGs
'''

from osgeo import gdal
import os
import easygui as eg
import sys
from pathlib import Path
from datetime import datetime
import logging
gdal.UseExceptions()


GUI_TITLE = 'Image Compressor'
ARCHIVE = 'Compressed Archive Image'
COG = 'Cloud Optimized Geotiff'
THUMBS = 'JPEG Thumbnail'


def archive_image(image_file, outpath):
    filename = os.path.basename(image_file)
    out_file = os.path.join(outpath, filename)

    ds = gdal.Translate(out_file, image_file, options="-co COMPRESS=LZW -co PREDICTOR=2 -co NUM_THREADS=ALL_CPUS")


def create_cog(image_file, outpath):
    filename = os.path.basename(image_file)
    out_file = os.path.join(outpath, filename)

    ds = gdal.Translate(out_file, image_file, options="-co COMPRESS=JPEG -co QUALITY=95 -co OVERVIEWS=AUTO -of COG -co NUM_THREADS=ALL_CPUS")


def create_thumbnail(image_file, outpath):
    filename = os.path.basename(image_file)
    filename, extension = os.path.splitext(filename)
    out_file = os.path.join(outpath, filename+'.thumb.jpg')

    gdal.Translate(out_file, image_file, options="-of JPEG -outsize 6.25% 0")


def select_output_options():
    question = 'Select output formats'

    choices = eg.multchoicebox(question, GUI_TITLE, [ARCHIVE, COG, THUMBS])
    if not choices:
        sys.exit()
    return choices


def select_directories(output_choices):
    input_msg = 'Select input directory'
    input_dir = eg.diropenbox(input_msg, GUI_TITLE)
    if not input_dir:
        sys.exit()

    output_directory_dict = {}
    for output_choice in output_choices:
        output_msg = f'Select output directory for: {output_choice}s'
        output_dir = eg.diropenbox(output_msg, GUI_TITLE)

        while input_dir == output_dir:
            eg.msgbox('The output directory must be a different location than the input directory')
            output_dir = eg.diropenbox(output_msg, GUI_TITLE)

        while output_dir in output_directory_dict.values() or output_dir == input_dir:
            eg.msgbox('The output directory must be different from previously selected directories')
            output_dir = eg.diropenbox(output_msg, GUI_TITLE)

        if not output_dir:
            sys.exit()

        output_directory_dict[output_choice] = output_dir

    return input_dir, output_directory_dict


def get_image_list(input_dir):
    indir = Path(input_dir)
    file_list = indir.rglob('*.tif')
    file_list = [str(f) for f in file_list]

    return file_list


def check_log_file(start_time, log_file):
    log_file_edited = False

    log_file_mod_time = os.path.getmtime(log_file)
    log_file_mod_time = datetime.fromtimestamp(log_file_mod_time)

    if log_file_mod_time > start_time:
        log_file_edited = True

    return log_file_edited

    
if __name__=='__main__':
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    elif __file__:
        app_path = os.path.dirname(__file__)
    LOG_FILE = os.path.join(app_path, 'Image_Compressor_errors.log')

    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.ERROR,
    filename=LOG_FILE)


    choices = select_output_options()
    input_dir, output_dirs = select_directories(choices)
    images = get_image_list(input_dir)

    start_time = datetime.now()
    print(f'Start time - {start_time.strftime("%Y-%m-%d %H:%M:%S")}')

    for idx, image in enumerate(images, start=1):
        print(f"Processing image {idx} of {len(images)}", end='\r')
        for output_type, output_path in output_dirs.items():
            if output_type == ARCHIVE:
                func = archive_image
            if output_type == COG:
                func = create_cog
            if output_type == THUMBS:
                func = create_thumbnail

            try:
                func(image, output_path)
            except:
                logging.error(f'Problem encountered with {image}')

    errors_occurred = check_log_file(start_time, LOG_FILE)
    if errors_occurred:
        print('\n-----Errors occurred, please check log file-----')

    print(f'\nEnd time - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    os.system('pause')