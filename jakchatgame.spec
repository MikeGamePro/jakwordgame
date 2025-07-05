# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['jakchatgame.py'],
    pathex=[],
    binaries=[],
    datas=[],
   hiddenimports=[
    'comtypes',
    'comtypes.client',
    'comtypes.automation',
    'comtypes.gen',
    'comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0',
    'comtypes.stream'
],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='jakchatgame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
