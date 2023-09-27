# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


data_to_include = [
    ('geoid.jpg', '.'),
    ('C:\\Users\\hsteiner\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\osgeo\\data\proj\\proj.db', '.')
]


a = Analysis(['LiGeoidApp.py'],
             pathex=[],
             binaries=[],
             datas=data_to_include,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=['hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='LiGeoidApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='C:\\CODE_DEVELOPMENT\\_QC_repo_local_NJ_DD050861\\boilerplate\\ico\\BC.ico' )
