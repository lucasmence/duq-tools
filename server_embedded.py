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

import threading
import time

# ── Import Flask app ────────────────────────────────────────────────
from server import app, parse_args


def _wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait until the server is listening on the given host:port."""
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    return False


def main():
    import webview

    args = parse_args()
    host = args.host
    port = args.port
    use_https = args.https

    protocol = "https" if use_https else "http"
    display_host = host if host != "0.0.0.0" else "127.0.0.1"
    url = f"{protocol}://{display_host}:{port}"

    # ── Start Flask in a background thread ──────────────────────────
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

    # ── Wait for server to be ready ─────────────────────────────────
    _wait_for_server(display_host, port)

    # ── Create native desktop window with embedded browser ──────────
    _ = webview.create_window(
        title="duq-tools",
        url=url,                  # Pass URL string — respects CLI args
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
        gui=None,                 # Auto-detect (WebView2 on Windows)
        private_mode=False,
        debug=False,              # Never open DevTools in a separate window
    )

    # ── Cleanup when window is closed ──────────────────────────────
    server.shutdown()


if __name__ == "__main__":
    main()
