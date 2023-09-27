import os
from pathlib import Path
from shutil import copy2


# specify the directory where the files are located
src_dir = Path(R'\\142.36.252.188\Lidar Accessw')
# src_dir = Path(R'C:\projects\lidarBC\load_data\files')

# specify the base directory for the new directory structure
dst_dir = Path(R'\\objectstore.nrs.bcgov\gdwuts')

file_list = src_dir.rglob('*_pa.laz')
file_list = list(file_list)
file_cnt = len(file_list)


for idx, filename in enumerate(file_list, start=1):
    fname = filename.name.split('_')

    tile_num = fname[1][:3]
    tile = fname[1][:4]
    year = fname[8]

    dst_path = dst_dir / tile_num / tile / year / 'pointcloud' / filename.name

    try:
        if not dst_path.exists():
            print(f'Copying file {idx}/{file_cnt}')
            copy2(filename, dst_path)
            # print(filename)
        else:
            with open('C:\projects\lidarBC\load_data\copy_errors.log', 'a') as log:
                log.write(f'File not copied -- {filename}\n')
    except:
        with open('C:\projects\lidarBC\load_data\copy_errors.log', 'a') as log:
            log.write(f'Copy error -- {filename}\n')
