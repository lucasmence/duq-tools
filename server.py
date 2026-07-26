#!/usr/bin/env python3
"""
duq-tools Web Server
====================
Transforms the duq-tools project into an HTTP server with a tabbed interface.

Run:
    pip install -r requirements.txt
    python server.py                     # HTTP  on http://localhost:5000
    python server.py --https             # HTTPS on https://localhost:5000
    HTTPS=1 python server.py             # HTTPS via env var

The three tools are available as individual tabs:
    - Sprite Editor   -> /sprite-editor
    - Sprite Fusion   -> /sprite-fusion
    - Trigger Editor  -> /trigger-editor
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

from flask import Flask, render_template, send_from_directory, abort

# ── Project paths ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

TOOL_DIRS = {
    "sprite-editor":  BASE_DIR / "duq-sprite-editor",
    "sprite-fusion":  BASE_DIR / "duq-sprite-fusion",
    "trigger-editor": BASE_DIR / "duq-trigger-editor",
}

TOOL_META = [
    {
        "id": "sprite-editor",
        "name": "Sprite Editor",
        "description": "Create and edit 2D sprite textures & animations",
        "icon": "/sprite-editor/icon.png",
        "color": "#5b7aff",
    },
    {
        "id": "sprite-fusion",
        "name": "Sprite Fusion",
        "description": "Merge multiple PNG sprites into a single spritesheet",
        "icon": "/sprite-fusion/icon.png",
        "color": "#a6e22e",
    },
    {
        "id": "trigger-editor",
        "name": "Trigger Editor",
        "description": "Define map triggers, events, conditions and actions",
        "icon": "/trigger-editor/icon.png",
        "color": "#f92672",
    },
]

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


# ── Homepage ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", tools=TOOL_META)


# ── Tool routes (serve each tool's static files) ───────────────────────
def _serve_tool(tool_id: str, filename: str):
    """Serve a file from a tool's directory."""
    tool_dir = TOOL_DIRS.get(tool_id)
    if tool_dir is None or not tool_dir.is_dir():
        abort(404)
    # Default to index.html when directory is requested
    if not filename:
        filename = "index.html"
    return send_from_directory(str(tool_dir), filename)


# Create a route for each tool — use unique endpoint names to avoid collisions
for tool_id in TOOL_DIRS:
    app.add_url_rule(
        f"/{tool_id}/",
        endpoint=f"tool_{tool_id}_index",
        view_func=lambda filename="", tid=tool_id: _serve_tool(tid, filename),
    )
    app.add_url_rule(
        f"/{tool_id}/<path:filename>",
        endpoint=f"tool_{tool_id}_file",
        view_func=lambda filename, tid=tool_id: _serve_tool(tid, filename),
    )


# ── Favicon ────────────────────────────────────────────────────────────
@app.route("/favicon.ico")
def favicon():
    icon_path = BASE_DIR / "icon.png"
    if icon_path.exists():
        return send_from_directory(str(BASE_DIR), "icon.png")
    abort(404)


# ── Service Worker ────────────────────────────────────────────────────
@app.route("/sw.js")
def service_worker():
    """Serve the Service Worker from the static directory.
    Must be served from the root scope so it can control all pages."""
    sw_path = BASE_DIR / "static" / "sw.js"
    if sw_path.exists():
        response = send_from_directory(
            str(BASE_DIR / "static"), "sw.js"
        )
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"
        response.content_type = "application/javascript"
        return response
    abort(404)


# ── SSL / HTTPS helpers ───────────────────────────────────────────────

CERT_DIR = BASE_DIR / "certs"
CERT_FILE = CERT_DIR / "cert.pem"
KEY_FILE = CERT_DIR / "key.pem"


def _ensure_cert_dir():
    """Create the certs/ directory if it doesn't exist."""
    CERT_DIR.mkdir(parents=True, exist_ok=True)


def _certs_exist() -> bool:
    """Check if both cert and key files exist."""
    return CERT_FILE.exists() and KEY_FILE.exists()


def _generate_self_signed_cert() -> bool:
    """Generate a self-signed SSL certificate using openssl.

    Returns True if a valid cert is available (newly generated or already
    existing). Returns False on failure.

    The cert is wildcarded for localhost, 127.0.0.1, and 0.0.0.0
    so it works for local development.
    """
    _ensure_cert_dir()

    if _certs_exist():
        print(f"  ℹ️  Using existing certificate: {CERT_FILE}")
        return True

    print(f"  🔐 Generating self-signed SSL certificate...")

    # OpenSSL subject
    subject = "/C=BR/ST=Local/L=Dev/O=duq-tools/CN=localhost"

    # SAN (Subject Alternative Names) for broad local compat
    san = "DNS:localhost,DNS:127.0.0.1,DNS:0.0.0.0,IP:127.0.0.1,IP:0.0.0.0"

    cmd = [
        "openssl", "req", "-x509",
        "-newkey", "rsa:2048",
        "-keyout", str(KEY_FILE),
        "-out", str(CERT_FILE),
        "-days", "3650",              # 10 years
        "-nodes",                      # no passphrase
        "-subj", subject,
        "-addext", f"subjectAltName={san}",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  ✅ Certificate generated: {CERT_FILE}")
        print(f"  ✅ Private key generated:  {KEY_FILE}")
        print(f"  ⚠️  This is a self-signed cert — your browser will show a")
        print(f"     security warning. This is normal for local development.")
        print(f"     You can safely proceed (click 'Advanced' → 'Proceed').")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to generate certificate: {e.stderr}")
        print(f"  ℹ️  Falling back to HTTP.")
        return False
    except FileNotFoundError:
        print(f"  ❌ OpenSSL not found. Please install openssl or use HTTP.")
        return False

    return True


def _get_ssl_context():
    """Build an SSL context tuple (cert, key) for Flask, or None."""
    if not _certs_exist():
        if not _generate_self_signed_cert():
            return None
    return (str(CERT_FILE), str(KEY_FILE))


# ── Entry point ────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="duq-tools Web Server — Game Dev Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                  # HTTP  → http://localhost:5000
  python server.py --https          # HTTPS → https://localhost:5000
  HTTPS=1 python server.py          # HTTPS via environment variable
  python server.py --https --port 8443
        """,
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Enable HTTPS with an auto-generated self-signed certificate",
        default=os.environ.get("HTTPS", "0").lower() in ("1", "true", "yes"),
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="Port to bind to (default: 5000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.environ.get("DEBUG", "1").lower() in ("1", "true", "yes"),
        help="Enable debug mode (default: True)",
    )
    parser.add_argument(
        "--no-debug",
        action="store_false",
        dest="debug",
        help="Disable debug mode",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    host = args.host
    port = args.port
    debug = args.debug
    use_https = args.https

    protocol = "https" if use_https else "http"
    ssl_context = _get_ssl_context() if use_https else None

    # If we wanted HTTPS but cert generation failed, fall back gracefully
    if use_https and ssl_context is None:
        print(f"  ⚠️  HTTPS requested but certificate unavailable — falling back to HTTP")
        protocol = "http"

    print(f"╔══════════════════════════════════════════════╗")
    print(f"║         🎮  duq-tools  Web Server           ║")
    print(f"╠══════════════════════════════════════════════╣")
    print(f"║  Sprite Editor   → /sprite-editor           ║")
    print(f"║  Sprite Fusion   → /sprite-fusion           ║")
    print(f"║  Trigger Editor  → /trigger-editor          ║")
    print(f"╠══════════════════════════════════════════════╣")
    print(f"║  Open {protocol}://{host if host != '0.0.0.0' else 'localhost'}:{port}  ║")
    if use_https and ssl_context:
        print(f"║  🔒 HTTPS with self-signed certificate       ║")
    print(f"╚══════════════════════════════════════════════╝")

    app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)


if __name__ == "__main__":
    main()
