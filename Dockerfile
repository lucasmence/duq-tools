# ── duq-tools Web Server ─────────────────────────────────────────────────
# Uses Flask to serve all three tools (Sprite Editor, Sprite Fusion,
# Trigger Editor) from a single container.
#
# Build & Run:
#   docker build -t duq-tools .
#   docker run -p 5000:5000 duq-tools                    # HTTP
#   docker run -p 5443:5443 -e HTTPS=1 duq-tools          # HTTPS
#
# Or with docker-compose:
#   docker compose up

FROM python:3.11-slim

LABEL org.opencontainers.image.title="duq-tools"
LABEL org.opencontainers.image.description="Game Dev Toolkit — Sprite Editor, Sprite Fusion, Trigger Editor"
LABEL org.opencontainers.image.licenses="MIT"

# Avoid Python buffering and bytecode cache in container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    HTTPS=0 \
    DEBUG=0

WORKDIR /app

# Install system dependencies (OpenSSL for HTTPS cert generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY templates/ templates/
COPY static/ static/
COPY duq-sprite-editor/ duq-sprite-editor/
COPY duq-sprite-fusion/ duq-sprite-fusion/
COPY duq-trigger-editor/ duq-trigger-editor/
COPY icon.png .

# The app listens on one port (configurable via PORT env, default 5000).
# When HTTPS=1, the same port serves HTTPS with the self-signed cert.
EXPOSE 5000

# Healthcheck — verify the app responds (handles both HTTP and HTTPS)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "\
import ssl, urllib.request;\
port = ${PORT:-5000};\
proto = 'https' if ${HTTPS:-0} == '1' else 'http';\
ctx = ssl.create_default_context();\
ctx.check_hostname = False;\
ctx.verify_mode = ssl.CERT_NONE;\
urllib.request.urlopen(f'{proto}://localhost:{port}/', timeout=3, context=ctx)\
"

ENTRYPOINT ["python3", "server.py", "--no-debug"]
