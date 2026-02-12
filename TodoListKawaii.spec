# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para TODO List Kawaii
# Genera un único .exe con el icono incluido. Ejecutar: pyinstaller TodoListKawaii.spec

import os

block_cipher = None

# Carpeta del proyecto (donde está el .spec y main.py)
project_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(project_dir, 'main.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'icono_unicornio.png'), '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkcalendar',
        'pytz',
        'schedule',
        'dateutil',
        'dateutil.tz',
        'pystray',
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TodoListKawaii',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # Sin ventana de consola (app gráfica)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_dir, 'icono_unicornio.ico') if os.path.isfile(os.path.join(project_dir, 'icono_unicornio.ico')) else None,
)
