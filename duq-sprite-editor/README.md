# Duq Sprite Editor

A browser-based editor for creating and editing 2D game sprite textures in JSON format. Designed for game engines that use JSON-based texture definitions with sprite sheets.

## Features

- **Texture Properties** — Define texture names, dimensions, light properties, and motion trail settings.
- **Animation Editor** — Add, remove, and configure sprite animations with adjustable direction bounds, frame limits, range, speed, looping, and sound references.
- **Spritesheet Preview** — Load a sprite sheet image and preview bounding boxes and frame regions overlaid directly on the sheet.
- **Animation Preview** — Play back individual animations in a floating popup to verify frame ranges and timing.
- **JSON Preview** — See the generated JSON output in real time as you edit, with validation for required fields.
- **Project Management** — Save and reopen projects (`.duq-project` files), set a project directory, and manage recently opened projects.
- **File Operations** — Open, edit, and save JSON texture files via the File System Access API or standard file picker.

## Usage

1. Open `index.html` in a modern browser (Chrome or Edge recommended for full File System Access API support).
2. Click **New Project** or open an existing JSON/project file.
3. Fill in the texture properties and add animations.
4. Load a sprite sheet (PNG) to preview frame regions.
5. Click **Save** to export the JSON texture definition.

## Project Structure

```
├── index.html       — Main application layout
├── css/styles.css   — Dark-themed UI styles
├── js/app.js        — Application logic
└── README.md        — This file
```

## Tech Stack

Plain HTML, CSS, and JavaScript — no frameworks or build tools required.
