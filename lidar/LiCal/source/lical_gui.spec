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

software_name = "LiCal v. 3.4.3"


block_cipher = None

a = Analysis(
    ['lical_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
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
    console=True ,
    icon='C:\\CODE_DEVELOPMENT\\_QC_repo_local_NJ_DD050861\\boilerplate\\ico\\BC.ico'
)
