# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.compat import is_darwin
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

datas = collect_data_files('doubleblind')

a = Analysis(
    ['doubleblind_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if is_darwin:
    exe_contents = (pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],)
    exe_kwargs = dict(icon='doubleblind/favicon.icns')
else:
    exe_contents = (pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],)
    exe_kwargs = dict(icon='doubleblind/favicon.ico')

exe = EXE(
    *exe_contents,
    **exe_kwargs,
    name='DoubleBlind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


# if not is_darwin:
#     coll = COLLECT(
#         exe,
#         splash.binaries,
#         a.binaries,
#         a.zipfiles,
#         a.datas,
#         strip=False,
#         upx=True,
#         upx_exclude=[],
#         name='DoubleBlind-1.1.0',
#     )