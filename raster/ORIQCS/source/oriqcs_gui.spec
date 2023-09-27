# ------------------------------------------------------------------------------
# How to create executables
#
# Instructions for using this .spec file to create an executable
# in the RSGE wiki:
#
# https://bcgov.sharepoint.com/teams/01112/_layouts/OneNote.aspx?id=%2Fteams%2F01112%2FShared%20Documents%2FQC%20Team%2FRSGE%20Wiki&wd=target%28Python%2FMaking%20Executables%20%28.exe%5C%29.one%7C10000CB6-8674-4968-A78A-52FE5089DAE5%2F0.%20Making%20Executables%3A%20Introduction%7C9CEC57FB-34F4-417F-B6E8-D349251100C5%2F%29
#
# ------------------------------------------------------------------------------

# -*- mode: python ; coding: utf-8 -*-

from glob import glob
import os

block_cipher = None

# ------------------------------------------------------------------------------
# Variables to update and/or confirm before compiling
# ------------------------------------------------------------------------------

# 1. software_name will be the name of the .exe file.
Version number also needs to be updated in oriqcs_gui.py.
software_name = 'ORIQCS_v.2.1.8'

# 2. python_environment_path is the path to the python environment or virtual
# environment for ORIQCS.
# How to tell this variable points to the correct folder:
#   - This folder contains some children folders, including Lib, and Scripts.
#   - It must be the same environment that you've been using to test ORIQCS,
#       otherwise the .exe may not compile, or it may not work once compiled.
python_environment_path = 'C:\\CODE_DEVELOPMENT\\_QC_repo_local_NJ_DD050861\\virtual_environments_natalie\\RSGE_aardvark'
python_environment_site_packages_folder = os.path.join(python_environment_path, 'Lib', 'site-packages')

# 3. Reminders before compiling:
#   - Update software version (_software_name()) in oriqcs_gui.py
#   - Ensure oriqcs_testing = False in oriqcs_gui.py

# ------------------------------------------------------------------------------
# Hidden imports
# ------------------------------------------------------------------------------

hidden_imports = [
    'rasterio._shim',
    'fiona._shim',
    'fiona.schema'
]

# Add all the .py files in rasterio to the hidden imports list.
# Reference:
# https://stackoverflow.com/questions/53149750/something-wrong-with-how-im-bundling-rasterio-into-an-executable
rasterio_dir = os.path.join(python_environment_site_packages_folder, 'rasterio')
rasterio_imports_paths = glob(
    os.path.join(rasterio_dir, '*.py')
)
for module in rasterio_imports_paths:
    module_filename = os.path.split(module)[-1]
    module_filename = 'rasterio.' + module_filename.replace('.py', '')
    hidden_imports.append(module_filename)


# ------------------------------------------------------------------------------
# Non-binary files to include
# ------------------------------------------------------------------------------

data_to_include = [
    (os.path.join(python_environment_site_packages_folder, 'osgeo\\data\\proj\\proj.db'), '.'),
    (os.path.join(python_environment_site_packages_folder, 'geopandas'),'geopandas'),
    (os.path.join(python_environment_site_packages_folder, 'geopandas\\datasets'), 'geopandas\\datasets')
]


# ------------------------------------------------------------------------------
# The usual .spec file class calls...  
#   - No need to change these class call; they use some of the variables
#   defined above as parameters.)
#   - To dive deeper to the inner workings of these classes, find their
#       code here:
#    <your python environment>/Lib/site-packages/PyInstaller/building/api.py
# ------------------------------------------------------------------------------

a = Analysis(
    ['oriqcs_gui.py'],
    pathex=[],
    binaries=[],
    datas=data_to_include,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=['hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=software_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, 
    icon='C:\\CODE_DEVELOPMENT\\_QC_repo_local_NJ_DD050861\\boilerplate\\ico\\BC.ico'
)
