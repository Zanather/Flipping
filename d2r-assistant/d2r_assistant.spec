# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for D2R Inventory Assistant.
Bundles Flask app with templates, static files, and item database.
"""

import os

block_cipher = None
base_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(base_dir, 'app.py')],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'templates'), 'templates'),
        (os.path.join(base_dir, 'static'), 'static'),
        (os.path.join(base_dir, 'data', 'item_database.json'), 'data'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'jinja2',
        'jinja2.ext',
        'markupsafe',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.debug',
        'click',
        'itsdangerous',
        'blinker',
        'config',
        'inventory_manager',
        'item_analyzer',
        'price_engine',
        'trade_integration',
        'community_tools',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'cryptography',
        'cffi',
        '_cffi_backend',
        'PIL',
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'tkinter',
        'test',
        'unittest',
        'xmlrpc',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='D2R_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='D2R_Assistant',
)
