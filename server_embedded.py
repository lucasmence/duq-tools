#!/usr/bin/env python3
"""
duq-tools Desktop Launcher (Embedded Browser)
===============================================
Starts the Flask web server and opens it in a native window with an embedded
WebView2 browser (Windows 10/11 native). No console window required.

Uses pywebview to create the desktop window:
    pip install pywebview

Build with PyInstaller using:
    pyinstaller build_embedded.spec --noconfirm --clean
"""

import sys
import os

# ── Import Flask app ────────────────────────────────────────────────
from server import app, parse_args


def main():
    import webview

    args = parse_args()
    host = args.host
    port = args.port
    use_https = args.https
    debug = args.debug

    protocol = "https" if use_https else "http"
    display_host = host if host != "0.0.0.0" else "127.0.0.1"
    url = f"{protocol}://{display_host}:{port}"

    # ── Start Flask in background and create native window ─────────
    # pywebview manages the Flask server lifecycle internally when
    # the app object is passed directly — no threading needed.
    window = webview.create_window(
        title="duq-tools",
        url=app,                 # pywebview handles Flask natively
        width=1280,
        height=800,
        min_size=(900, 600),
        resizable=True,
        fullscreen=False,
        text_select=True,
        confirm_close=True,
    )

    # Start the GUI event loop (blocks until window is closed)
    webview.start(
        gui=None,                # Auto-detect (WebView2 on Windows)
        private_mode=False,
        debug=debug,
    )


if __name__ == "__main__":
    main()
