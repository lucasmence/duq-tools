# 🪟 Building duq-tools for Windows

This project supports two methods for building a standalone `duq-tools.exe` for
Windows 10 / 11 using [PyInstaller](https://pyinstaller.org/).

## Method 1: GitHub Actions (recommended)

The easiest way — no local setup needed.

1. Push a tag matching `v*` (e.g. `v1.0.0`):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. The **Release** workflow automatically:
   - Runs tests
   - Builds the Docker image
   - **Builds `duq-tools.exe`** on a Windows runner via PyInstaller
   - Attaches the `.exe` to the GitHub Release page

👉 Download the `.exe` from the **Releases** section of the repository.

### Pull request check

Every pull request also runs a **Windows build check** to ensure the `.exe`
still compiles — without uploading artifacts.

---

## Method 2: Local build (Windows only)

You need a Windows machine with Python 3.8+ installed.

### Quick build (one command)

Open **Command Prompt** in the project root and run:

```
build_windows.bat
```

The script will:
1. Upgrade pip
2. Install project dependencies
3. Install PyInstaller
4. Build `duq-tools.exe` into the `dist/` folder

### Manual build (step by step)

```batch
REM 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM 2. Build the executable
pyinstaller build.spec --noconfirm --clean

REM 3. Find the .exe in:
REM    dist\duq-tools.exe
```

---

## Running the executable

| Command | Description |
|---------|-------------|
| `duq-tools.exe` | Start HTTP server on port 5000 |
| `duq-tools.exe --https` | Start HTTPS with auto-generated cert |
| `duq-tools.exe --port 8080` | Custom port |
| `duq-tools.exe --no-debug` | Production mode (no debug) |
| `duq-tools.exe --help` | Show all options |

Open `http://localhost:5000` (or the URL shown in the console) in your browser.

---

## Notes

- The `.exe` is **standalone** (~30–50 MB) — no Python installation needed.
- Console window is shown so you can see server logs and URLs.
- The first time you use `--https`, a self-signed certificate is auto-generated
  (requires OpenSSL to be installed on the system).
- The `build.spec` file excludes heavy/unused modules (PySide6, tkinter, test
  suites) to keep the bundle size reasonable.
