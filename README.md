# 🎮 duq-tools

[![Docker Build & Test](https://github.com/duqtools/duq-tools/actions/workflows/docker.yml/badge.svg)](https://github.com/duqtools/duq-tools/actions/workflows/docker.yml)
[![Tests](https://github.com/duqtools/duq-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/duqtools/duq-tools/actions/workflows/tests.yml)
[![Dependabot](https://img.shields.io/badge/dependabot-enabled-025e8c?logo=dependabot&logoColor=white)](https://github.com/duqtools/duq-tools/security/dependabot)
[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://python.org)

**Game Dev Toolkit** — Three sprite & trigger editors in one place.

| Tool | Description |
|------|-------------|
| 🎨 **Sprite Editor** | Create and edit 2D sprite textures & animations |
| 🔀 **Sprite Fusion** | Merge multiple PNG sprites into a single spritesheet |
| ⚡ **Trigger Editor** | Define map triggers, events, conditions and actions |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (HTTP)
python3 server.py

# Or with HTTPS
python3 server.py --https
```

Then open **http://localhost:5000** in your browser.

## 🐳 Docker

```bash
# Build and run with Docker Compose
docker compose up

# Or build manually
docker build -t duq-tools .
docker run -p 5000:5000 duq-tools
```

## 🔒 HTTPS

```bash
# Auto-generates a self-signed SSL certificate
python3 server.py --https
HTTPS=1 python3 server.py
```

Certificate is stored in `certs/` and reused across restarts.
