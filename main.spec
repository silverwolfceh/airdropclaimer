# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import shutil
import os
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

PROGRAM_NAME = "AutoClaimAirdrop"
PROGRAM_FILE = "main.py"
ICON_FILE = "icon.png"

def post_build():
    # Copying supported file
    dest = os.path.join("dist", PROGRAM_NAME)
    supported_file = ["config.json", "ua.json", "proxy.txt", "docs/confighelper.html", "docs/data.js", "update/updater.exe"]
    for d in supported_file:
        shutil.copy(d, dest)

    # Create modules dir
    dest = os.path.join("dist", PROGRAM_NAME, "_internal", "modules")
    os.makedirs(dest)

    # List all .py file
    all_files = os.listdir("modules")
    py_files = [file for file in all_files if file.endswith('.py')]
    for p in py_files:
        srcfile = os.path.join("modules", p)
        shutil.copy(srcfile, dest)

a = Analysis(
    [PROGRAM_FILE],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['pytz'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=PROGRAM_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=PROGRAM_NAME,
    icon=ICON_FILE
)

post_build()  # Call the function to copy additional files