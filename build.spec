# -*- mode: python ; coding: utf-8 -*-
"""
duq-tools PyInstaller Specification
====================================
Builds a single-file Windows executable of the Flask web server.

Usage (Windows):
    pip install -r requirements.txt pyinstaller
    pyinstaller build.spec

The resulting .exe will be in dist/duq-tools.exe.
It bundles all static assets, templates, and tool directories.
"""

import sys
from pathlib import Path

block_cipher = None

# ── Collect all data directories ──────────────────────────────────────
# These must mirror the directory layout expected by server.py
DATA_DIRS = [
    ("templates", "templates"),
    ("static", "static"),
    ("duq-sprite-editor", "duq-sprite-editor"),
    ("duq-sprite-fusion", "duq-sprite-fusion"),
    ("duq-trigger-editor", "duq-trigger-editor"),
]

# Build datas list using Tree for recursive inclusion
datas = []
for src, dst in DATA_DIRS:
    src_path = Path.cwd() / src
    if src_path.is_dir():
        datas.append((str(src_path), dst))

# Also include icon files at the root
icon_png = Path.cwd() / "icon.png"
if icon_png.exists():
    datas.append((str(icon_png), "."))

icon_ico = Path.cwd() / "icon.ico"
if icon_ico.exists():
    datas.append((str(icon_ico), "."))

# Determine which icon to use for the executable
# Windows .ico is preferred, fall back to .png
icon_exe = icon_ico if icon_ico.exists() else icon_png

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    ["server.py"],
    pathex=[str(Path.cwd())],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Flask and its dependencies
        "flask",
        "werkzeug",
        "jinja2",
        "markupsafe",
        "itsdangerous",
        "click",
        # PIL/Pillow (imported by some tools)
        "PIL",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Unnecessary modules to reduce bundle size
        "PySide6",
        "PyQt5",
        "PyQt6",
        "tkinter",
        "unittest",
        "pytest",
        "email",
        "http.cookiejar",
        "http.cookies",
        "xml.etree",
        "xml.dom",
        "test",
        "distutils",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ archive ──────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Executable ───────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="duq-tools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,          # Show console window for server output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_exe) if icon_exe.exists() else None,
)
