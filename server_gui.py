#!/usr/bin/env python3
"""
duq-tools GUI Launcher
=======================
Starts the Flask web server in the background, opens the default browser,
and shows a simple message box. No console window required.

Build with PyInstaller using:
    pyinstaller build_gui.spec --noconfirm --clean
"""

import sys
import os
import threading
import time
import webbrowser

# ── Import server logic ──────────────────────────────────────────────
from server import app, parse_args


def _open_browser(url: str, delay: float = 1.5):
    """Open the browser after a short delay to let the server start."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass  # Browser might not be available, that's OK


def main():
    args = parse_args()
    host = args.host
    port = args.port
    debug = args.debug
    use_https = args.https

    protocol = "https" if use_https else "http"
    display_host = host if host != "0.0.0.0" else "localhost"
    url = f"{protocol}://{display_host}:{port}"

    # ── Start the Flask server in a background thread ───────────────
    from werkzeug.serving import make_server

    ssl_context = None
    if use_https:
        from server import _get_ssl_context
        ssl_context = _get_ssl_context()
        if ssl_context is None:
            protocol = "http"
            url = f"http://{display_host}:{port}"

    server = make_server(host, port, app, ssl_context=ssl_context)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # ── Open browser ────────────────────────────────────────────────
    threading.Thread(target=_open_browser, args=(url,), daemon=True).start()

    # ── Show message box (Windows) or console message ────────────────
    title = "duq-tools"
    message = (
        f"duq-tools is running!\n\n"
        f"🌐 {url}\n\n"
        f"The browser has been opened.\n"
        f"Click OK to stop the server."
    )

    try:
        # Windows native message box (no console needed)
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0)
    except (AttributeError, ImportError):
        # Fallback for non-Windows platforms / testing
        print(message)
        print("\nPress Ctrl+C to stop the server.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # ── Shutdown ────────────────────────────────────────────────────
    server.shutdown()


if __name__ == "__main__":
    main()
