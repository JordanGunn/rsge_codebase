# -*- mode: python -*-

block_cipher = None


a = Analysis(
    ['GNSS_backup_check.py'],
    pathex=['D:\\QC_Tools\\Python\\___python_projects_qc__\\Misc\\GNSS_backup'],
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
    name='GNSS_backup_check',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True ,
    icon='C:\\CODE_DEVELOPMENT\\_QC_repo_local_NJ_DD050861\\boilerplate\\ico\\BC.ico'
)
