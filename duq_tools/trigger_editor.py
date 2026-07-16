"""
Trigger Editor Tab — Pseudo-language ↔ JSON Converter & Editor.
Port of duq-trigger-editor from web to PySide6.
"""

import json
import re
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QPlainTextEdit, QFileDialog, QMessageBox, QSplitter, QTextBrowser,
    QListWidget, QListWidgetItem, QAbstractItemView, QMenu,
    QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPoint
from PySide6.QtGui import (
    QFont, QColor, QPainter, QSyntaxHighlighter, QTextCharFormat,
    QTextCursor, QKeySequence, QTextDocument, QShortcut
)


# ─── Language Spec ───────────────────────────────────────────────────────────

EVENT_TYPES = {
    'initialization', 'unit-kill', 'region-between-units', 'dialog-box-close',
    'unit-cast-ability', 'distance-between-units', 'unit-use-item', 'call-event',
    'region-entered', 'item-dropped', 'item-picked'
}

CONDITION_TYPES = {
    'game-event-check', 'unit-check-target', 'unit-check-stats', 'dialog-box-option',
    'get-game-context', 'unit-check-target-ability-hotkey', 'unit-check-used-item',
    'player-control-type', 'get-global-variable', 'unit-check-alive', 'region-check-item',
    'region-check-unit', 'unit-player-check-item', 'map-check-visited', 'unit-check-type',
    'unit-check-picked-item', 'unit-check-casted-ability'
}

ACTION_TYPES = {
    'game-event-change', 'camera-move-unit', 'camera-lock-hero', 'menu-show',
    'system-sleep', 'text-dialog', 'unit-intelligence-range-min-change',
    'set-gold-all-players', 'text-messagebox', 'text-dialogbox',
    'add-gold-all-players', 'spawn-item', 'add-item', 'trigger-reset',
    'remove-skill-all', 'remove-passive-all', 'clear-storage', 'add-skill',
    'add-passive', 'disable-skill', 'set-game-context', 'unit-edit-status',
    'spawn-unit', 'spawn-unit-region', 'unit-edit-exp', 'unit-pause',
    'unit-unpause', 'add-special-effect', 'unit-teleport', 'unit-kill',
    'unit-remove', 'unit-change-name', 'item-remove', 'unit-cast-skill',
    'spawn-merchant', 'merchant-remove', 'merchant-remove-all',
    'merchant-update', 'unit-mass-enemy-kill', 'unit-mass-kill-type',
    'delete-save', 'game-select-subclass', 'unit-hide', 'unit-unhide',
    'add-sfx', 'play-animation', 'call-event', 'prop-play-animation',
    'environment-play-animation', 'camera-move-prop', 'camera-move-region',
    'camera-shake', 'play-sound', 'portal-enable', 'set-global-variable',
    'prop-kill', 'block-map-teleport', 'unit-cast-skill-region',
    'unit-teleport-region', 'unit-move-unit', 'unit-move-region',
    'spawn-item-region', 'region-terrain-animation', 'region-terrain-remove',
    'apply-map-fog', 'break-map-fog', 'music-change', 'spawn-environment',
    'music-pause', 'travel-block', 'unit-set-dialog-value', 'wall-remove',
    'check-official-custom-map', 'check-campaign-endgame', 'check-campaign-final',
    'change-mass-environment', 'change-map-particles', 'show-help-tooltip',
    'reset-unit', 'remove-skills-hotkey', 'add-environment-sfx',
    'add-environment-sfx-region', 'enable-skill-tree', 'clear-skill-tree',
    'clear-passive-tree', 'set-food', 'move-all-items-region',
    'take-all-items-region', 'minimap-disable', 'environment-play-animation-region',
    'add-wall', 'fog-toggle', 'add-intro-sound', 'play-intro-sound',
    'erase-world', 'exit', 'show-credits-label', 'toggle-control',
    'toggle-extra-modes', 'extra-modes-info'
}

META_KEYS = [
    'item-drop', 'item-drop-list', 'procedural', 'procedural-list',
    'procedural-room-size', 'procedural-exit-door', 'unit-spawn-range',
    'unit-spawn-limit', 'unit-spawn', 'merchant-spawn-chance', 'merchant-spawn',
    'exit', 'special-exits-chance', 'special-exits', 'list-items-spawn',
    'list-food-spawn', 'environments-drop', 'environments-drop-hit',
    'list-chests-spawn', 'list-shrines-spawn', 'musics'
]

KEYWORDS = {'on', 'if', 'and', 'or', 'then', 'true', 'false'}


# ─── Syntax Highlighter ─────────────────────────────────────────────────────

class TriggerHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the trigger pseudo-language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # Comments (// ...)
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#75715e"))
        comment_fmt.setFontItalic(True)
        self._rules.append((r'//.*', comment_fmt))

        # Meta keys (@key)
        meta_fmt = QTextCharFormat()
        meta_fmt.setForeground(QColor("#fd971f"))
        meta_fmt.setFontWeight(QFont.Bold)
        self._rules.append((r'@\w+', meta_fmt))

        # Keywords (on, if, and, or, then, true, false)
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#f92672"))
        keyword_fmt.setFontWeight(QFont.Bold)
        for kw in KEYWORDS:
            self._rules.append((r'\b' + re.escape(kw) + r'\b', keyword_fmt))

        # Event types
        event_fmt = QTextCharFormat()
        event_fmt.setForeground(QColor("#66d9ef"))
        for et in EVENT_TYPES:
            self._rules.append((r'\b' + re.escape(et) + r'\b', event_fmt))

        # Condition types
        cond_fmt = QTextCharFormat()
        cond_fmt.setForeground(QColor("#ae81ff"))
        for ct in CONDITION_TYPES:
            self._rules.append((r'\b' + re.escape(ct) + r'\b', cond_fmt))

        # Action types
        action_fmt = QTextCharFormat()
        action_fmt.setForeground(QColor("#a6e22e"))
        for at in ACTION_TYPES:
            self._rules.append((r'\b' + re.escape(at) + r'\b', action_fmt))

        # Named keys (unit:, float:, int:, etc.)
        named_key_fmt = QTextCharFormat()
        named_key_fmt.setForeground(QColor("#a1efe4"))
        self._rules.append((r'\b(unit|float|int|string|bool):\s*', named_key_fmt))

        # Strings ("...")
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#e6db74"))
        self._rules.append((r'"[^"]*"', string_fmt))

        # Numbers
        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#fd971f"))
        self._rules.append((r'\b\d+\.?\d*\b', number_fmt))

        # Booleans
        bool_fmt = QTextCharFormat()
        bool_fmt.setForeground(QColor("#ae81ff"))
        self._rules.append((r'\b(true|false)\b', bool_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)


# ─── Compiler ────────────────────────────────────────────────────────────────

class TriggerCompiler:
    """Compiles trigger pseudo-language to JSON."""

    def compile(self, text: str) -> dict:
        """Parse the pseudo-language and return JSON structure."""
        result = {
            "trigger": [],
            "item-drop": [],
            "item-drop-list": [],
        }

        lines = text.split('\n')
        current_trigger = None
        in_conditions = False
        in_actions = False

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('//'):
                i += 1
                continue

            # Meta keys
            if line.startswith('@'):
                key, _, value = line[1:].partition(':')
                key = key.strip()
                value = value.strip().strip('"')
                if key in META_KEYS:
                    result[key] = value
                i += 1
                continue

            # on <event>
            if line.startswith('on '):
                if current_trigger:
                    result["trigger"].append(current_trigger)
                current_trigger = {"events": [], "conditions": [], "then": []}
                in_conditions = False
                in_actions = False

                event_str = line[3:].strip()
                event = self._parse_event(event_str)
                if event:
                    current_trigger["events"].append(event)
                i += 1

                # Check for if conditions on next lines
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('if '):
                        in_conditions = True
                        cond_str = next_line[3:].strip()
                        cond = self._parse_condition(cond_str)
                        if cond:
                            current_trigger["conditions"].append(cond)
                        i += 1
                    elif next_line.startswith('then:'):
                        in_actions = True
                        in_conditions = False
                        i += 1
                        # Collect actions
                        while i < len(lines):
                            action_line = lines[i].strip()
                            if action_line and not action_line.startswith('//'):
                                action = self._parse_action(action_line)
                                if action:
                                    current_trigger["then"].append(action)
                            i += 1
                        break
                    else:
                        break
                continue

            i += 1

        # Add last trigger
        if current_trigger:
            # Clean up empty conditions
            if not current_trigger["conditions"]:
                del current_trigger["conditions"]
            result["trigger"].append(current_trigger)

        return result

    def _parse_event(self, text: str) -> dict:
        """Parse an event line like 'unit-kill(unit: "boss-1")'."""
        match = re.match(r'(\S+)\s*\((.*)\)\s*$', text)
        if match:
            event_type = match.group(1)
            args_str = match.group(2)
            event = {"event": event_type}
            self._parse_args(event, args_str)
            return event
        else:
            return {"event": text.strip()}

    def _parse_condition(self, text: str) -> dict:
        """Parse a condition line like 'get-game-context("start")'."""
        # Handle 'and'/'or' separated conditions
        parts = re.split(r'\s+(?:and|or)\s+', text)
        conditions = []
        for part in parts:
            part = part.strip()
            match = re.match(r'(\S+)\s*\((.*)\)\s*$', part)
            if match:
                cond_type = match.group(1)
                args_str = match.group(2)
                cond = {"condition": cond_type}
                self._parse_args(cond, args_str)
                conditions.append(cond)
        return conditions[0] if len(conditions) == 1 else conditions

    def _parse_action(self, text: str) -> dict:
        """Parse an action line like 'system-sleep(1.0)'."""
        match = re.match(r'(\S+)\s*\((.*)\)\s*$', text)
        if match:
            action_type = match.group(1)
            args_str = match.group(2)
            action = {"action": action_type}
            self._parse_args(action, args_str)
            return action
        return {"action": text.strip()}

    def _parse_args(self, obj: dict, args_str: str):
        """Parse arguments into the object."""
        if not args_str.strip():
            return

        # Split by comma, respecting quotes
        args = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', args_str)

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue

            # Named argument: key: value
            named_match = re.match(r'(\w+):\s*(.*)', arg)
            if named_match:
                key = named_match.group(1)
                value = named_match.group(2).strip()

                if key == 'unit':
                    obj["unitName"] = self._parse_value(value)
                elif key == 'float':
                    obj["floatValue"] = float(self._parse_value(value))
                elif key == 'int':
                    obj["integerValue"] = int(self._parse_value(value))
                elif key == 'string':
                    self._add_to_array(obj, "strings", self._parse_value(value))
                elif key == 'bool':
                    self._add_to_array(obj, "booleans", self._parse_value(value))
            else:
                # Positional argument
                value = self._parse_value(arg)
                if isinstance(value, str):
                    self._add_to_array(obj, "strings", value)
                elif isinstance(value, float):
                    self._add_to_array(obj, "floats", value)
                elif isinstance(value, int):
                    self._add_to_array(obj, "integers", value)

    def _parse_value(self, value: str):
        """Parse a value string to appropriate Python type."""
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _add_to_array(self, obj: dict, key: str, value):
        """Add a value to an array field in the object."""
        if key not in obj:
            obj[key] = []
        obj[key].append({"value": value})


# ─── Editor Widget ───────────────────────────────────────────────────────────

class TriggerEditorWidget(QWidget):
    """Main Trigger Editor widget with syntax highlighting and compilation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.compiler = TriggerCompiler()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #161922; border-bottom: 1px solid #2a2f45; padding: 8px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        open_btn = QPushButton("📂 Open")
        open_btn.clicked.connect(self._open_file)
        toolbar_layout.addWidget(open_btn)

        save_btn = QPushButton("💾 Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_file)
        toolbar_layout.addWidget(save_btn)

        toolbar_layout.addSpacing(16)

        compile_btn = QPushButton("⚡ Compile")
        compile_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #ff4d6a;
                border: 1px solid #ff4d6a; border-radius: 6px;
                padding: 8px 16px; font-weight: 600;
            }
            QPushButton:hover { background: rgba(255, 77, 106, 0.15); }
        """)
        compile_btn.clicked.connect(self._compile)
        toolbar_layout.addWidget(compile_btn)

        docs_btn = QPushButton("📖 Docs")
        docs_btn.clicked.connect(self._show_docs)
        toolbar_layout.addWidget(docs_btn)

        toolbar_layout.addStretch()

        title = QLabel("⚡ Trigger Editor")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #5b7aff;")
        toolbar_layout.addWidget(title)

        layout.addWidget(toolbar)

        # Main content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left: Code editor
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Gutter + Editor
        editor_container = QWidget()
        editor_container_layout = QHBoxLayout(editor_container)
        editor_container_layout.setContentsMargins(0, 0, 0, 0)
        editor_container_layout.setSpacing(0)

        # Line numbers
        self.line_numbers = QLabel()
        self.line_numbers.setStyleSheet("""
            QLabel {
                background-color: #1e1f1c;
                color: #49483e;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                font-size: 14px;
                line-height: 1.6;
                padding: 10px 8px 10px 12px;
                border-right: 1px solid #3e3d32;
            }
        """)
        self.line_numbers.setFixedWidth(52)
        self.line_numbers.setAlignment(Qt.AlignRight | Qt.AlignTop)
        editor_container_layout.addWidget(self.line_numbers)

        # Code editor
        self.code_editor = QPlainTextEdit()
        self.code_editor.setFont(QFont("Cascadia Code, Fira Code, Consolas", 14))
        self.code_editor.setTabStopDistance(32)
        self.code_editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.code_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1b1c18;
                color: #f8f8f2;
                border: none;
                padding: 10px 16px;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                font-size: 14px;
                line-height: 1.6;
                selection-background-color: rgba(249, 38, 114, 0.3);
            }
        """)
        self.code_editor.setPlaceholderText("Open a JSON file or start writing trigger script...\n\non initialization\n    then:\n        system-sleep(1.0)")

        # Apply syntax highlighter
        self.highlighter = TriggerHighlighter(self.code_editor.document())

        # Connect signals
        self.code_editor.textChanged.connect(self._update_line_numbers)
        self.code_editor.cursorPositionChanged.connect(self._update_cursor_info)

        editor_container_layout.addWidget(self.code_editor)
        editor_layout.addWidget(editor_container)

        content_layout.addWidget(editor_panel, 2)

        # Right: Preview / Output
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        # Preview header
        preview_header = QFrame()
        preview_header.setStyleSheet("background-color: #161922; border-bottom: 1px solid #2a2f45; padding: 8px 12px;")
        preview_header_layout = QHBoxLayout(preview_header)
        preview_header_layout.setContentsMargins(12, 8, 12, 8)

        self.preview_title = QLabel("JSON Output")
        self.preview_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        preview_header_layout.addWidget(self.preview_title)
        preview_header_layout.addStretch()

        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(self._copy_json)
        preview_header_layout.addWidget(copy_btn)

        preview_layout.addWidget(preview_header)

        # JSON output
        self.json_output = QPlainTextEdit()
        self.json_output.setReadOnly(True)
        self.json_output.setFont(QFont("Cascadia Code, Fira Code, Consolas", 13))
        self.json_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1b1c18;
                color: #f8f8f2;
                border: none;
                padding: 16px;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                font-size: 13px;
            }
        """)
        preview_layout.addWidget(self.json_output)

        content_layout.addWidget(preview_panel, 1)

        layout.addWidget(content)

        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #161922; border-top: 1px solid #2a2f45; padding: 4px 12px;")
        status_bar_layout = QHBoxLayout(status_bar)
        status_bar_layout.setContentsMargins(12, 4, 12, 4)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #a6e22e; font-size: 8px;")
        status_bar_layout.addWidget(self.status_dot)

        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet("color: #75715e; font-size: 11px;")
        status_bar_layout.addWidget(self.status_text)

        status_bar_layout.addStretch()

        self.cursor_info = QLabel("Ln 1, Col 1")
        self.cursor_info.setStyleSheet("color: #75715e; font-size: 11px;")
        status_bar_layout.addWidget(self.cursor_info)

        self.char_count = QLabel("0 chars")
        self.char_count.setStyleSheet("color: #75715e; font-size: 11px;")
        status_bar_layout.addWidget(self.char_count)

        layout.addWidget(status_bar)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self, self._open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_file)
        QShortcut(QKeySequence("Ctrl+D"), self, self._show_docs)

    def _update_line_numbers(self):
        """Update line numbers display."""
        text = self.code_editor.toPlainText()
        lines = text.count('\n') + 1
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.setText(line_numbers_text)
        self.char_count.setText(f"{len(text)} chars")

    def _update_cursor_info(self):
        """Update cursor position display."""
        cursor = self.code_editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_info.setText(f"Ln {line}, Col {col}")

    def _open_file(self):
        """Open a JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Convert JSON to pseudo-language (simplified)
                text = self._json_to_text(data)
                self.code_editor.setPlainText(text)
                self.status_text.setText(f"Opened: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def _save_file(self):
        """Save the current content."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "trigger.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                # Compile and save as JSON
                data = self.compiler.compile(self.code_editor.toPlainText())
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                self.status_text.setText(f"Saved: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def _compile(self):
        """Compile the pseudo-language to JSON."""
        try:
            text = self.code_editor.toPlainText()
            data = self.compiler.compile(text)
            json_str = json.dumps(data, indent=4)
            self.json_output.setPlainText(json_str)
            self.status_dot.setStyleSheet("color: #a6e22e; font-size: 8px;")
            self.status_text.setText("Compiled successfully")
        except Exception as e:
            self.json_output.setPlainText(f"Compilation error:\n{e}")
            self.status_dot.setStyleSheet("color: #f92672; font-size: 8px;")
            self.status_text.setText("Compilation failed")

    def _show_docs(self):
        """Show documentation in a dialog."""
        from PySide6.QtWidgets import QDialog, QTextBrowser

        dialog = QDialog(self)
        dialog.setWindowTitle("Trigger Editor Documentation")
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1b1c18;
                color: #f8f8f2;
                border: none;
                padding: 20px;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
            }
        """)

        docs_html = self._get_docs_html()
        browser.setHtml(docs_html)
        layout.addWidget(browser)

        dialog.exec()

    def _get_docs_html(self) -> str:
        """Generate comprehensive documentation HTML matching the web version."""
        events_list = ''.join(
            f'<li><code>{et}</code></li>' for et in sorted(EVENT_TYPES)
        )
        conditions_list = ''.join(
            f'<li><code>{ct}</code></li>' for ct in sorted(CONDITION_TYPES)
        )
        actions_list = ''.join(
            f'<li><code>{at}</code></li>' for at in sorted(ACTION_TYPES)
        )
        meta_list = ''.join(
            f'<li><code>@{mk}</code></li>' for mk in META_KEYS
        )
        return f"""
        <h1 style="color: #f92672;">Trigger System Documentation</h1>
        <p style="color: #75715e;">Ported from the web-based Duq Trigger Editor</p>

        <h2 style="color: #66d9ef;">Syntax Overview</h2>
        <pre style="background: #2d2e2a; padding: 12px; border-radius: 4px; color: #f8f8f2;">
on &lt;event-type&gt;[(args)]
    [if &lt;condition-type&gt;(args) [and/or &lt;condition-type&gt;(args) ...]]
        then:
            &lt;action-type&gt;(args)
        </pre>
        <p><b>Comments:</b> Lines starting with <code>//</code> are ignored.</p>

        <h2 style="color: #a1efe4;">Named Arguments</h2>
        <p>Arguments use named keys to specify types:</p>
        <table>
            <tr><th>Syntax</th><th>Type</th><th>Example</th></tr>
            <tr><td><code>unit: "name"</code></td><td>Unit name string</td><td><code>unit: "hero"</code></td></tr>
            <tr><td><code>float: 1.5</code></td><td>Float value</td><td><code>float: 200.0</code></td></tr>
            <tr><td><code>int: 10</code></td><td>Integer value</td><td><code>int: 1</code></td></tr>
            <tr><td><code>string: "text"</code></td><td>String value</td><td><code>string: "start"</code></td></tr>
            <tr><td><code>bool: true</code></td><td>Boolean value</td><td><code>bool: true</code></td></tr>
        </table>
        <p><b>Positional arguments</b> are auto-typed: <code>"text"</code> → string, <code>123</code> → int, <code>1.5</code> → float.</p>

        <hr>

        <h2 style="color: #66d9ef;">Events ({len(EVENT_TYPES)} types)</h2>
        <p>Events define <b>what</b> triggers a script. Events use <b>OR logic</b>: any one event fires → check conditions.</p>
        <ul>{events_list}</ul>
        <h3 style="color: #66d9ef;">Event Examples</h3>
        <table>
            <tr><th>Event</th><th>Syntax</th><th>Fields</th></tr>
            <tr><td><code>initialization</code></td><td><code>on initialization</code></td><td>None — fires on map load</td></tr>
            <tr><td><code>unit-kill</code></td><td><code>on unit-kill(unit: "boss")</code></td><td><code>unitName</code></td></tr>
            <tr><td><code>region-between-units</code></td><td><code>on region-between-units(float: 200, unit: "enemy")</code></td><td><code>unitName</code>, <code>floatValue</code></td></tr>
            <tr><td><code>distance-between-units</code></td><td><code>on distance-between-units(float: 500, unit: "hero")</code></td><td><code>unitName</code>, <code>floatValue</code></td></tr>
            <tr><td><code>region-entered</code></td><td><code>on region-entered(int: 10, unit: "hero")</code></td><td><code>unitName</code>, <code>integerValue</code></td></tr>
            <tr><td><code>dialog-box-close</code></td><td><code>on dialog-box-close</code></td><td>None</td></tr>
            <tr><td><code>unit-cast-ability</code></td><td><code>on unit-cast-ability</code></td><td>None</td></tr>
            <tr><td><code>unit-use-item</code></td><td><code>on unit-use-item</code></td><td>None</td></tr>
            <tr><td><code>call-event</code></td><td><code>on call-event</code></td><td>None — triggered by <code>call-event</code> action</td></tr>
            <tr><td><code>item-dropped</code></td><td><code>on item-dropped</code></td><td>None</td></tr>
            <tr><td><code>item-picked</code></td><td><code>on item-picked</code></td><td>None</td></tr>
        </table>
        <p><b>Note:</b> Events watch specific units update their reference each frame to handle destroyed/recreated units.</p>

        <hr>

        <h2 style="color: #ae81ff;">Conditions ({len(CONDITION_TYPES)} types)</h2>
        <p>Conditions use <b>AND logic</b> — every condition must pass. If a trigger has no conditions, it always fires.</p>
        <ul>{conditions_list}</ul>
        <h3 style="color: #ae81ff;">Condition Examples</h3>
        <table>
            <tr><th>Condition</th><th>Syntax</th><th>Description</th></tr>
            <tr><td><code>game-event-check</code></td><td><code>if game-event-check(int: 2)</code></td><td>Check game event ID</td></tr>
            <tr><td><code>unit-check-target</code></td><td><code>if unit-check-target(unit: "hero")</code></td><td>Check unit name</td></tr>
            <tr><td><code>unit-check-stats</code></td><td><code>if unit-check-stats("health", "lower", float: 50)</code></td><td>Compare stat</td></tr>
            <tr><td><code>dialog-box-option</code></td><td><code>if dialog-box-option(int: 1, int: 2)</code></td><td>Check dialog option</td></tr>
            <tr><td><code>get-game-context</code></td><td><code>if get-game-context("battle")</code></td><td>Check context string</td></tr>
            <tr><td><code>get-global-variable</code></td><td><code>if get-global-variable("boss-1", true)</code></td><td>Check global var</td></tr>
            <tr><td><code>unit-check-alive</code></td><td><code>if unit-check-alive("hero", true)</code></td><td>Check alive status</td></tr>
            <tr><td><code>region-check-item</code></td><td><code>if region-check-item("key", int: 10)</code></td><td>Check item in region</td></tr>
            <tr><td><code>region-check-unit</code></td><td><code>if region-check-unit("hero", int: 10)</code></td><td>Check unit in region</td></tr>
            <tr><td><code>unit-player-check-item</code></td><td><code>if unit-player-check-item("hero", "sword")</code></td><td>Check inventory item</td></tr>
            <tr><td><code>map-check-visited</code></td><td><code>if map-check-visited("village")</code></td><td>Check map visited</td></tr>
            <tr><td><code>unit-check-type</code></td><td><code>if unit-check-type("characters/boss/lich")</code></td><td>Check unit type</td></tr>
            <tr><td><code>unit-check-picked-item</code></td><td><code>if unit-check-picked-item("sword")</code></td><td>Check picked item</td></tr>
            <tr><td><code>unit-check-casted-ability</code></td><td><code>if unit-check-casted-ability(int: 7)</code></td><td>Check casted ability</td></tr>
            <tr><td><code>unit-check-used-item</code></td><td><code>if unit-check-used-item("potion")</code></td><td>Check used item</td></tr>
            <tr><td><code>unit-check-target-ability-hotkey</code></td><td><code>if unit-check-target-ability-hotkey(int: 1)</code></td><td>Check ability hotkey</td></tr>
            <tr><td><code>player-control-type</code></td><td><code>if player-control-type(int: 0)</code></td><td>Check control mode</td></tr>
        </table>

        <hr>

        <h2 style="color: #a6e22e;">Actions ({len(ACTION_TYPES)} types)</h2>
        <p>Actions execute sequentially in the order they appear under <code>then:</code>.</p>
        <ul>{actions_list}</ul>
        <h3 style="color: #a6e22e;">Action Examples by Category</h3>

        <p style="color: #f92672;"><b>Game Flow</b></p>
        <table>
            <tr><td><code>game-event-change(int, ?bool)</code></td><td>Change game event</td></tr>
            <tr><td><code>system-sleep(float)</code></td><td>Pause for duration</td></tr>
            <tr><td><code>call-event()</code></td><td>Chain to another trigger</td></tr>
            <tr><td><code>trigger-reset()</code></td><td>Allow trigger to fire again</td></tr>
        </table>

        <p style="color: #f92672;"><b>Camera</b></p>
        <table>
            <tr><td><code>camera-move-unit(unit, ?float)</code></td><td>Move camera to unit</td></tr>
            <tr><td><code>camera-lock-hero(?bool)</code></td><td>Lock/unlock camera</td></tr>
            <tr><td><code>camera-move-prop(unit, ?float)</code></td><td>Camera to prop</td></tr>
            <tr><td><code>camera-move-region(int, ?float)</code></td><td>Camera to region</td></tr>
            <tr><td><code>camera-shake(float)</code></td><td>Shake camera</td></tr>
        </table>

        <p style="color: #f92672;"><b>Units</b></p>
        <table>
            <tr><td><code>spawn-unit(path, alliance, ?name, ?drop, x, y, ?group)</code></td><td>Spawn unit at position</td></tr>
            <tr><td><code>spawn-unit-region(path, alliance, ?name, ?drop, region)</code></td><td>Spawn at region</td></tr>
            <tr><td><code>unit-kill(unit)</code></td><td>Kill unit</td></tr>
            <tr><td><code>unit-remove(unit)</code></td><td>Remove unit</td></tr>
            <tr><td><code>unit-hide(unit, float)</code></td><td>Hide unit</td></tr>
            <tr><td><code>unit-unhide(unit)</code></td><td>Reveal unit</td></tr>
            <tr><td><code>unit-pause(unit, float)</code></td><td>Pause unit</td></tr>
            <tr><td><code>unit-unpause(unit)</code></td><td>Unpause unit</td></tr>
            <tr><td><code>unit-teleport(unit, x, y)</code></td><td>Teleport unit</td></tr>
            <tr><td><code>unit-teleport-region(unit, int)</code></td><td>Teleport to region</td></tr>
            <tr><td><code>unit-move-unit(unit, target)</code></td><td>Move to unit</td></tr>
            <tr><td><code>unit-move-region(unit, int)</code></td><td>Move to region</td></tr>
            <tr><td><code>unit-change-name(unit, name)</code></td><td>Rename unit</td></tr>
            <tr><td><code>unit-edit-exp(unit, int, ?add)</code></td><td>Edit XP</td></tr>
            <tr><td><code>unit-edit-status(unit, attr, values, ?useAttr, ?add)</code></td><td>Edit stats</td></tr>
            <tr><td><code>reset-unit(unit)</code></td><td>Reset to defaults</td></tr>
            <tr><td><code>unit-cast-skill(caster, target, skill, ?anim)</code></td><td>Cast skill at unit</td></tr>
            <tr><td><code>unit-cast-skill-region(caster, skill, region, ?anim)</code></td><td>Cast skill at region</td></tr>
            <tr><td><code>unit-intelligence-range-min-change(unit, float)</code></td><td>Change aggro range</td></tr>
            <tr><td><code>unit-mass-enemy-kill()</code></td><td>Kill all enemies</td></tr>
            <tr><td><code>unit-mass-kill-type(path)</code></td><td>Kill all of type</td></tr>
        </table>

        <p style="color: #f92672;"><b>Items</b></p>
        <table>
            <tr><td><code>spawn-item(items, ?stack, ?x, ?y)</code></td><td>Spawn item at position</td></tr>
            <tr><td><code>spawn-item-region(items, ?stack, region)</code></td><td>Spawn item at region</td></tr>
            <tr><td><code>add-item(items, ?stack)</code></td><td>Add to inventory</td></tr>
            <tr><td><code>item-remove(name)</code></td><td>Remove item from world</td></tr>
        </table>

        <p style="color: #f92672;"><b>UI / Text</b></p>
        <table>
            <tr><td><code>text-messagebox(args...)</code></td><td>Show message box</td></tr>
            <tr><td><code>text-dialogbox(args...)</code></td><td>Open dialog with options</td></tr>
            <tr><td><code>text-dialog(unit, id, key, ?useDialogBox)</code></td><td>Floating dialog</td></tr>
            <tr><td><code>menu-show(?fullReset)</code></td><td>Show menu</td></tr>
        </table>

        <p style="color: #f92672;"><b>Audio</b></p>
        <table>
            <tr><td><code>music-change(name)</code></td><td>Change background music</td></tr>
            <tr><td><code>music-pause()</code></td><td>Pause music</td></tr>
            <tr><td><code>play-sound(path)</code></td><td>Play sound effect</td></tr>
        </table>

        <p style="color: #f92672;"><b>Effects</b></p>
        <table>
            <tr><td><code>add-sfx(path, ?x, ?y, ?region)</code></td><td>Add special effect</td></tr>
            <tr><td><code>add-special-effect(texture, anim, attach, target, x, y)</code></td><td>Add complex effect</td></tr>
            <tr><td><code>play-animation(unit, anim, ?loop)</code></td><td>Play unit animation</td></tr>
            <tr><td><code>prop-play-animation(prop, anim)</code></td><td>Play prop animation</td></tr>
            <tr><td><code>environment-play-animation(env, anim)</code></td><td>Play environment animation</td></tr>
        </table>

        <hr>

        <h2 style="color: #e6db74;">Meta Keys</h2>
        <p>Meta keys configure map-level properties. Use <code>@key: value</code> at the top of the script.</p>
        <ul>{meta_list}</ul>
        <table>
            <tr><th>Key</th><th>Syntax</th><th>Description</th></tr>
            <tr><td><code>@item-drop</code></td><td><code>@item-drop: "name"</code></td><td>Named loot drop table</td></tr>
            <tr><td><code>@procedural</code></td><td><code>@procedural: true</code></td><td>Enable procedural generation</td></tr>
            <tr><td><code>@exit</code></td><td><code>@exit: "map/path"</code></td><td>Default exit map</td></tr>
            <tr><td><code>@unit-spawn-range</code></td><td><code>@unit-spawn-range: 500</code></td><td>Unit spawn range</td></tr>
            <tr><td><code>@unit-spawn-limit</code></td><td><code>@unit-spawn-limit: 10</code></td><td>Max spawned units</td></tr>
            <tr><td><code>@merchant-spawn-chance</code></td><td><code>@merchant-spawn-chance: 0.25</code></td><td>Merchant spawn chance</td></tr>
            <tr><td><code>@special-exits-chance</code></td><td><code>@special-exits-chance: 0.25</code></td><td>Special exit chance</td></tr>
        </table>

        <hr>

        <h2 style="color: #f92672;">Full Example</h2>
        <pre style="background: #2d2e2a; padding: 12px; border-radius: 4px; color: #f8f8f2;">
// Map initialization trigger
on initialization
    if get-game-context("start")
        then:
            set-gold-all-players(int: 500)
            text-messagebox(string: "Welcome!")

// When the boss dies
on unit-kill(unit: "boss-1")
    then:
            system-sleep(float: 2.0)
            spawn-unit("units/treasure", int: 0, float: 100, float: 200)
            call-event()

// Chain trigger
on call-event
    if get-game-context("boss-defeated")
        then:
            portal-enable(int: 1, bool: true)
        </pre>

        <hr>
        <p style="color: #75715e; font-size: 11px;">
            Documentation ported from the web-based Duq Trigger Editor.<br>
            Full reference available at the project repository.
        </p>
        """

    def _json_to_text(self, data: dict) -> str:
        """Convert JSON data to pseudo-language text (simplified)."""
        lines = []

        # Meta keys
        for key in META_KEYS:
            if key in data:
                value = data[key]
                if isinstance(value, bool):
                    lines.append(f"@{key}: {str(value).lower()}")
                elif isinstance(value, str):
                    lines.append(f'@{key}: "{value}"')
                else:
                    lines.append(f"@{key}: {value}")

        lines.append("")

        # Triggers
        for trigger in data.get("trigger", []):
            events = trigger.get("events", [])
            conditions = trigger.get("conditions", [])
            actions = trigger.get("then", [])

            for event in events:
                event_type = event.get("event", "")
                args = []
                if "unitName" in event:
                    args.append(f'unit: "{event["unitName"]}"')
                if "floatValue" in event:
                    args.append(f'float: {event["floatValue"]}')
                if "integerValue" in event:
                    args.append(f'int: {event["integerValue"]}')

                args_str = ", ".join(args)
                if args_str:
                    lines.append(f"on {event_type}({args_str})")
                else:
                    lines.append(f"on {event_type}")

            for cond in conditions:
                if isinstance(cond, list):
                    for c in cond:
                        cond_type = c.get("condition", "")
                        args = self._condition_args_to_text(c)
                        lines.append(f"    if {cond_type}({args})")
                else:
                    cond_type = cond.get("condition", "")
                    args = self._condition_args_to_text(cond)
                    lines.append(f"    if {cond_type}({args})")

            lines.append("    then:")
            for action in actions:
                action_type = action.get("action", "")
                args = self._action_args_to_text(action)
                if args:
                    lines.append(f"        {action_type}({args})")
                else:
                    lines.append(f"        {action_type}()")

            lines.append("")

        return "\n".join(lines)

    def _condition_args_to_text(self, cond: dict) -> str:
        """Convert condition arguments to text."""
        args = []
        if "unitName" in cond:
            args.append(f'unit: "{cond["unitName"]}"')
        if "floatValue" in cond:
            args.append(f'float: {cond["floatValue"]}')
        if "integerValue" in cond:
            args.append(f'int: {cond["integerValue"]}')
        for s in cond.get("strings", []):
            args.append(f'"{s["value"]}"')
        for i in cond.get("integers", []):
            args.append(f'int: {i["value"]}')
        for f in cond.get("floats", []):
            args.append(f'float: {f["value"]}')
        for b in cond.get("booleans", []):
            args.append(f'bool: {str(b["value"]).lower()}')
        return ", ".join(args)

    def _action_args_to_text(self, action: dict) -> str:
        """Convert action arguments to text."""
        args = []
        if "unitName" in action:
            args.append(f'unit: "{action["unitName"]}"')
        if "integerValue" in action:
            args.append(f'int: {action["integerValue"]}')
        if "floatValue" in action:
            args.append(f'float: {action["floatValue"]}')
        for s in action.get("strings", []):
            args.append(f'"{s["value"]}"')
        for i in action.get("integers", []):
            args.append(f'int: {i["value"]}')
        for f in action.get("floats", []):
            args.append(f'float: {f["value"]}')
        for b in action.get("booleans", []):
            args.append(f'bool: {str(b["value"]).lower()}')
        return ", ".join(args)

    def _copy_json(self):
        """Copy JSON output to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.json_output.toPlainText())
