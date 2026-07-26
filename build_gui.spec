# -*- mode: python ; coding: utf-8 -*-
"""
duq-tools GUI PyInstaller Specification
=========================================
Builds a windowed (no console) Windows executable that starts the Flask
server, opens the browser, and shows a message box.

Usage (Windows):
    pip install -r requirements.txt pyinstaller
    pyinstaller build_gui.spec

The resulting .exe will be in dist/duq-tools-gui.exe.
"""

import sys
from pathlib import Path

block_cipher = None

# ── Collect all data directories ──────────────────────────────────────
DATA_DIRS = [
    ("templates", "templates"),
    ("static", "static"),
    ("duq-sprite-editor", "duq-sprite-editor"),
    ("duq-sprite-fusion", "duq-sprite-fusion"),
    ("duq-trigger-editor", "duq-trigger-editor"),
]

datas = []
for src, dst in DATA_DIRS:
    src_path = Path.cwd() / src
    if src_path.is_dir():
        datas.append((str(src_path), dst))

icon_png = Path.cwd() / "icon.png"
if icon_png.exists():
    datas.append((str(icon_png), "."))

icon_ico = Path.cwd() / "icon.ico"
if icon_ico.exists():
    datas.append((str(icon_ico), "."))

icon_exe = icon_ico if icon_ico.exists() else icon_png

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    ["server_gui.py"],
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
        # server module is imported by server_gui.py
        "server",
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

# ── Executable (windowed — no console) ───────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="duq-tools-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,         # No console window — runs as GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_exe) if icon_exe.exists() else None,
)
