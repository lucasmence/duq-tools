"""
Sprite Editor Tab — JSON texture editor for 2D game sprites.
Port of duq-sprite-editor from web to PySide6.
"""

import json
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QCheckBox, QPushButton, QTextEdit, QScrollArea,
    QFrame, QFileDialog, QMessageBox, QSplitter, QGridLayout,
    QPlainTextEdit, QGroupBox, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QSyntaxHighlighter, QTextCharFormat


# ─── Default Animation Template ──────────────────────────────────────────────
DEFAULT_ANIMATION = {
    "name": "",
    "spriteDirectionLeft": 0,
    "spriteDirectionTop": 0,
    "spriteDirectionWidth": 96,
    "spriteDirectionHeight": 96,
    "spriteLimit": 288,
    "spriteRange": 96,
    "animated": True,
    "reverseMode": False,
    "loop": True,
    "sideFlip": True,
    "speed": 0.25,
    "sound": ""
}

REQUIRED_ANIMATIONS = ["stand"]


class JSONHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # JSON key
        key_fmt = QTextCharFormat()
        key_fmt.setForeground(QColor("#9cdcfe"))
        self._rules.append((r'"[^"]*"\s*:', key_fmt))

        # String value
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#ce9178"))
        self._rules.append((r':\s*"[^"]*"', str_fmt))

        # Number
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#b5cea8"))
        self._rules.append((r':\s*-?\d+\.?\d*', num_fmt))

        # Boolean
        bool_fmt = QTextCharFormat()
        bool_fmt.setForeground(QColor("#569cd6"))
        self._rules.append((r':\s*(true|false)', bool_fmt))

        # Null
        null_fmt = QTextCharFormat()
        null_fmt.setForeground(QColor("#569cd6"))
        self._rules.append((r':\s*null', null_fmt))

        # Brackets
        bracket_fmt = QTextCharFormat()
        bracket_fmt.setForeground(QColor("#d4d4d4"))
        self._rules.append((r'[\[\]\{\}]', bracket_fmt))

        # Punctuation
        punct_fmt = QTextCharFormat()
        punct_fmt.setForeground(QColor("#808080"))
        self._rules.append((r'[,:\s]', punct_fmt))

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self._rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)


class AnimationCard(QFrame):
    """Widget representing a single animation entry."""

    changed = Signal()
    removed = Signal(int)

    def __init__(self, index: int, data: dict, is_required: bool = False, parent=None):
        super().__init__(parent)
        self.index = index
        self.data = data.copy()
        self.is_required = is_required
        self.setObjectName("animationCard")
        self.setStyleSheet("""
            QFrame#animationCard {
                background-color: #1c2030;
                border: 1px solid #2a2f45;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            QFrame#animationCard:hover {
                border-color: #3a3f55;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        # Indicator dot
        self.indicator = QLabel("●")
        self.indicator.setStyleSheet("color: #34d399; font-size: 10px;")
        header.addWidget(self.indicator)

        # Name label
        self.name_label = QLabel(data.get("name", "(unnamed)") or "(unnamed)")
        self.name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.addWidget(self.name_label)

        # Required badge
        if is_required:
            badge = QLabel("required")
            badge.setStyleSheet("""
                font-size: 10px; padding: 2px 6px; border-radius: 4px;
                background-color: rgba(91, 122, 255, 0.12); color: #5b7aff;
            """)
            header.addWidget(badge)

        header.addStretch()

        # Remove button
        if not is_required:
            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #ff4d6a; border: none;
                    border-radius: 4px; font-size: 14px;
                }
                QPushButton:hover { background: rgba(255, 77, 106, 0.15); }
            """)
            remove_btn.clicked.connect(lambda: self.removed.emit(self.index))
            header.addWidget(remove_btn)

        layout.addLayout(header)

        # Form grid
        grid = QGridLayout()
        grid.setSpacing(8)

        row = 0

        # Animation Name
        grid.addWidget(self._label("Animation Name"), row, 0, 1, 2)
        self.name_input = QLineEdit(data.get("name", ""))
        self.name_input.setPlaceholderText("e.g. walk, attack, death")
        if is_required:
            self.name_input.setReadOnly(True)
        self.name_input.textChanged.connect(self._on_name_changed)
        grid.addWidget(self.name_input, row + 1, 0, 1, 2)
        row += 2

        # Sprite Left / Top
        grid.addWidget(self._label("Sprite Left"), row, 0)
        self.left_input = QSpinBox()
        self.left_input.setRange(0, 99999)
        self.left_input.setValue(data.get("spriteDirectionLeft", 0))
        self.left_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.left_input, row + 1, 0)

        grid.addWidget(self._label("Sprite Top"), row, 1)
        self.top_input = QSpinBox()
        self.top_input.setRange(0, 99999)
        self.top_input.setValue(data.get("spriteDirectionTop", 0))
        self.top_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.top_input, row + 1, 1)
        row += 2

        # Sprite Width / Height
        grid.addWidget(self._label("Sprite Width"), row, 0)
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 99999)
        self.width_input.setValue(data.get("spriteDirectionWidth", 96))
        self.width_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.width_input, row + 1, 0)

        grid.addWidget(self._label("Sprite Height"), row, 1)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 99999)
        self.height_input.setValue(data.get("spriteDirectionHeight", 96))
        self.height_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.height_input, row + 1, 1)
        row += 2

        # Sprite Limit / Range
        grid.addWidget(self._label("Sprite Limit"), row, 0)
        self.limit_input = QSpinBox()
        self.limit_input.setRange(0, 99999)
        self.limit_input.setValue(data.get("spriteLimit", 288))
        self.limit_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.limit_input, row + 1, 0)

        grid.addWidget(self._label("Sprite Range"), row, 1)
        self.range_input = QSpinBox()
        self.range_input.setRange(1, 99999)
        self.range_input.setValue(data.get("spriteRange", 96))
        self.range_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.range_input, row + 1, 1)
        row += 2

        # Speed
        grid.addWidget(self._label("Speed"), row, 0)
        self.speed_input = QDoubleSpinBox()
        self.speed_input.setRange(0.0, 100.0)
        self.speed_input.setSingleStep(0.01)
        self.speed_input.setValue(data.get("speed", 0.25))
        self.speed_input.valueChanged.connect(self._on_changed)
        grid.addWidget(self.speed_input, row + 1, 0)

        # Sound (optional)
        grid.addWidget(self._label("Sound (optional)"), row, 1)
        self.sound_input = QLineEdit(data.get("sound", ""))
        self.sound_input.setPlaceholderText("e.g. units/skeleton-death")
        self.sound_input.textChanged.connect(self._on_changed)
        grid.addWidget(self.sound_input, row + 1, 1)
        row += 2

        # Checkboxes
        self.animated_cb = QCheckBox("Animated")
        self.animated_cb.setChecked(data.get("animated", True))
        self.animated_cb.stateChanged.connect(self._on_changed)
        grid.addWidget(self.animated_cb, row, 0)

        self.reverse_cb = QCheckBox("Reverse Mode")
        self.reverse_cb.setChecked(data.get("reverseMode", False))
        self.reverse_cb.stateChanged.connect(self._on_changed)
        grid.addWidget(self.reverse_cb, row, 1)

        self.loop_cb = QCheckBox("Loop")
        self.loop_cb.setChecked(data.get("loop", True))
        self.loop_cb.stateChanged.connect(self._on_changed)
        grid.addWidget(self.loop_cb, row + 1, 0)

        self.sideflip_cb = QCheckBox("Side Flip")
        self.sideflip_cb.setChecked(data.get("sideFlip", True))
        self.sideflip_cb.stateChanged.connect(self._on_changed)
        grid.addWidget(self.sideflip_cb, row + 1, 1)

        layout.addLayout(grid)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: #8b90a5; text-transform: uppercase; letter-spacing: 0.3px;")
        return lbl

    def _on_name_changed(self, text):
        self.name_label.setText(text or "(unnamed)")
        self._on_changed()

    def _on_changed(self):
        self.data = self.get_data()
        self.changed.emit()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "spriteDirectionLeft": self.left_input.value(),
            "spriteDirectionTop": self.top_input.value(),
            "spriteDirectionWidth": self.width_input.value(),
            "spriteDirectionHeight": self.height_input.value(),
            "spriteLimit": self.limit_input.value(),
            "spriteRange": self.range_input.value(),
            "animated": self.animated_cb.isChecked(),
            "reverseMode": self.reverse_cb.isChecked(),
            "loop": self.loop_cb.isChecked(),
            "sideFlip": self.sideflip_cb.isChecked(),
            "speed": self.speed_input.value(),
            "sound": self.sound_input.text().strip(),
        }


class SpriteEditorWidget(QWidget):
    """Main Sprite Editor widget with form, animations, and JSON preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left panel: Form + Animations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

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

        toolbar_layout.addStretch()

        title = QLabel("🎨 Sprite Editor")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #5b7aff;")
        toolbar_layout.addWidget(title)

        left_layout.addWidget(toolbar)

        # Scroll area for form + animations
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: #0f1117; }")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        # Texture Properties
        props_group = QGroupBox("Texture Properties")
        props_layout = QGridLayout(props_group)
        props_layout.setSpacing(10)

        row = 0

        # Texture Name (required)
        props_layout.addWidget(self._label("Texture Name *"), row, 0, 1, 2)
        self.texturename_input = QLineEdit()
        self.texturename_input.setPlaceholderText("e.g. units/player/barbarian")
        self.texturename_input.textChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.texturename_input, row + 1, 0, 1, 2)
        row += 2

        # Prop Generation
        props_layout.addWidget(self._label("Prop Generation"), row, 0)
        self.prop_generation_input = QLineEdit()
        self.prop_generation_input.setPlaceholderText("e.g. natural, scatter, uniform")
        self.prop_generation_input.textChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.prop_generation_input, row + 1, 0)

        # Texture Original Chance
        props_layout.addWidget(self._label("Texture Original Chance"), row, 1)
        self.texture_chance_input = QSpinBox()
        self.texture_chance_input.setRange(0, 100)
        self.texture_chance_input.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.texture_chance_input, row + 1, 1)
        row += 2

        # Front checkbox
        self.front_cb = QCheckBox("Front")
        self.front_cb.stateChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.front_cb, row, 0, 1, 2)
        row += 1

        # Light Color
        props_layout.addWidget(self._label("Light Color (RGBA)"), row, 0, 1, 4)
        row += 1
        color_layout = QHBoxLayout()
        self.light_r = QSpinBox(); self.light_r.setRange(0, 255); self.light_r.setPrefix("R: ")
        self.light_g = QSpinBox(); self.light_g.setRange(0, 255); self.light_g.setPrefix("G: ")
        self.light_b = QSpinBox(); self.light_b.setRange(0, 255); self.light_b.setPrefix("B: ")
        self.light_a = QSpinBox(); self.light_a.setRange(0, 255); self.light_a.setPrefix("A: ")
        for spin in [self.light_r, self.light_g, self.light_b, self.light_a]:
            spin.valueChanged.connect(self._update_json_preview)
            color_layout.addWidget(spin)
        props_layout.addLayout(color_layout, row, 0, 1, 4)
        row += 1

        # Light Range / Intensity
        props_layout.addWidget(self._label("Light Range"), row, 0)
        self.light_range = QDoubleSpinBox()
        self.light_range.setRange(0, 99999)
        self.light_range.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.light_range, row + 1, 0)

        props_layout.addWidget(self._label("Light Intensity"), row, 1)
        self.light_intensity = QDoubleSpinBox()
        self.light_intensity.setRange(0.0, 1.0)
        self.light_intensity.setSingleStep(0.01)
        self.light_intensity.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.light_intensity, row + 1, 1)
        row += 2

        # Dimensions
        props_layout.addWidget(self._label("Dimension Width"), row, 0)
        self.dim_width = QSpinBox()
        self.dim_width.setRange(1, 99999)
        self.dim_width.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.dim_width, row + 1, 0)

        props_layout.addWidget(self._label("Dimension Height"), row, 1)
        self.dim_height = QSpinBox()
        self.dim_height.setRange(1, 99999)
        self.dim_height.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.dim_height, row + 1, 1)
        row += 2

        # Motion Trail Frequency
        props_layout.addWidget(self._label("Motion Trail Frequency"), row, 0)
        self.trail_freq = QDoubleSpinBox()
        self.trail_freq.setRange(0, 99999)
        self.trail_freq.setSingleStep(0.001)
        self.trail_freq.valueChanged.connect(self._update_json_preview)
        props_layout.addWidget(self.trail_freq, row + 1, 0)

        form_layout.addWidget(props_group)

        # Animations Section
        anim_header = QHBoxLayout()
        anim_title = QLabel("Animations")
        anim_title.setObjectName("sectionTitle")
        anim_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #8b90a5; text-transform: uppercase; letter-spacing: 0.5px;")
        anim_header.addWidget(anim_title)
        anim_header.addStretch()

        add_anim_btn = QPushButton("+ Add Animation")
        add_anim_btn.clicked.connect(self._add_animation)
        anim_header.addWidget(add_anim_btn)

        form_layout.addLayout(anim_header)

        # Animations container
        self.animations_container = QWidget()
        self.animations_layout = QVBoxLayout(self.animations_container)
        self.animations_layout.setContentsMargins(0, 0, 0, 0)
        self.animations_layout.setSpacing(8)
        form_layout.addWidget(self.animations_container)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        left_layout.addWidget(scroll)

        # Right panel: JSON Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # JSON toolbar
        json_toolbar = QFrame()
        json_toolbar.setStyleSheet("background-color: #161922; border-bottom: 1px solid #2a2f45; padding: 8px;")
        json_toolbar_layout = QHBoxLayout(json_toolbar)
        json_toolbar_layout.setContentsMargins(12, 8, 12, 8)

        json_title = QLabel("JSON Preview")
        json_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        json_toolbar_layout.addWidget(json_title)

        json_toolbar_layout.addStretch()

        self.validation_badge = QLabel("✓ Valid")
        self.validation_badge.setObjectName("validationBadge")
        self.validation_badge.setStyleSheet("""
            font-size: 11px; padding: 4px 10px; border-radius: 12px;
            background-color: rgba(52, 211, 153, 0.12); color: #34d399;
        """)
        json_toolbar_layout.addWidget(self.validation_badge)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(self._copy_json)
        json_toolbar_layout.addWidget(copy_btn)

        right_layout.addWidget(json_toolbar)

        # JSON preview area
        self.json_preview = QPlainTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Cascadia Code, Fira Code, Consolas", 13))
        self.json_preview.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1b1c18; color: #f8f8f2;
                border: none; padding: 16px;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                font-size: 13px; line-height: 1.6;
            }
        """)
        right_layout.addWidget(self.json_preview)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)

        # Add default "stand" animation
        self._add_animation(name="stand", required=True)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: #8b90a5; text-transform: uppercase; letter-spacing: 0.3px;")
        return lbl

    def _add_animation(self, name: str = "new-animation", required: bool = False):
        """Add a new animation card."""
        data = DEFAULT_ANIMATION.copy()
        data["name"] = name

        is_required = name in REQUIRED_ANIMATIONS or required
        card = AnimationCard(len(self.animations), data, is_required)
        card.changed.connect(self._update_json_preview)
        card.removed.connect(self._remove_animation)
        self.animations_layout.addWidget(card)
        self.animations.append(card)
        self._update_json_preview()

    def _remove_animation(self, index: int):
        """Remove an animation by index."""
        if 0 <= index < len(self.animations):
            card = self.animations.pop(index)
            self.animations_layout.removeWidget(card)
            card.deleteLater()
            # Re-index remaining cards
            for i, c in enumerate(self.animations):
                c.index = i
            self._update_json_preview()

    def _build_json(self) -> dict:
        """Build JSON data from form fields."""
        data = {}

        tn = self.texturename_input.text().strip()
        if tn:
            data["texturename"] = tn

        pg = self.prop_generation_input.text().strip()
        if pg:
            data["prop-generation"] = pg

        tc = self.texture_chance_input.value()
        if tc > 0:
            data["texture-original-chance"] = tc

        data["front"] = self.front_cb.isChecked()

        # Light color
        r, g, b, a = self.light_r.value(), self.light_g.value(), self.light_b.value(), self.light_a.value()
        if r or g or b or a:
            data["light-color"] = {"red": r, "green": g, "blue": b, "alpha": a}

        lr = self.light_range.value()
        if lr:
            data["light-range"] = lr

        li = self.light_intensity.value()
        if li:
            data["light-intensity"] = li

        dw = self.dim_width.value()
        if dw:
            data["dimension-width"] = dw

        dh = self.dim_height.value()
        if dh:
            data["dimension-height"] = dh

        tf = self.trail_freq.value()
        if tf:
            data["motion-trail-frequency"] = tf

        # Animations
        anims = []
        for card in self.animations:
            anim_data = card.get_data()
            entry = {
                "sprite-direction-left": anim_data["spriteDirectionLeft"],
                "sprite-direction-top": anim_data["spriteDirectionTop"],
                "sprite-direction-width": anim_data["spriteDirectionWidth"],
                "sprite-direction-height": anim_data["spriteDirectionHeight"],
                "sprite-limit": anim_data["spriteLimit"],
                "sprite-range": anim_data["spriteRange"],
                "animated": anim_data["animated"],
                "reverse-mode": anim_data["reverseMode"],
                "loop": anim_data["loop"],
                "side-flip": anim_data["sideFlip"],
                "speed": anim_data["speed"],
                "name": anim_data["name"] or "unnamed",
            }
            if anim_data["sound"]:
                entry["sound"] = anim_data["sound"]
            anims.append(entry)

        if anims:
            data["animation"] = anims

        return data

    def _update_json_preview(self):
        """Update the JSON preview text."""
        data = self._build_json()
        json_str = json.dumps(data, indent=4)
        self.json_preview.setPlainText(json_str)

        # Validate
        has_name = bool(self.texturename_input.text().strip())
        has_stand = any(c.name_input.text().strip() == "stand" for c in self.animations)
        valid = has_name and has_stand

        if valid:
            self.validation_badge.setText("✓ Valid")
            self.validation_badge.setStyleSheet("""
                font-size: 11px; padding: 4px 10px; border-radius: 12px;
                background-color: rgba(52, 211, 153, 0.12); color: #34d399;
            """)
        else:
            errors = []
            if not has_name:
                errors.append("texturename required")
            if not has_stand:
                errors.append("animation 'stand' required")
            self.validation_badge.setText("✗ " + ", ".join(errors))
            self.validation_badge.setStyleSheet("""
                font-size: 11px; padding: 4px 10px; border-radius: 12px;
                background-color: rgba(255, 77, 106, 0.12); color: #ff4d6a;
            """)

    def _open_file(self):
        """Open a JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._load_from_json(data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def _load_from_json(self, data: dict):
        """Load data from a JSON object into the form."""
        self.texturename_input.setText(data.get("texturename", ""))
        self.prop_generation_input.setText(data.get("prop-generation", ""))
        self.texture_chance_input.setValue(data.get("texture-original-chance", 0))
        self.front_cb.setChecked(data.get("front", False))

        lc = data.get("light-color", {})
        self.light_r.setValue(lc.get("red", 0))
        self.light_g.setValue(lc.get("green", 0))
        self.light_b.setValue(lc.get("blue", 0))
        self.light_a.setValue(lc.get("alpha", 0))

        self.light_range.setValue(data.get("light-range", 0))
        self.light_intensity.setValue(data.get("light-intensity", 0))
        self.dim_width.setValue(data.get("dimension-width", 0))
        self.dim_height.setValue(data.get("dimension-height", 0))
        self.trail_freq.setValue(data.get("motion-trail-frequency", 0))

        # Clear existing animations
        for card in self.animations[:]:
            self.animations_layout.removeWidget(card)
            card.deleteLater()
        self.animations.clear()

        # Load animations
        for anim_data in data.get("animation", []):
            name = anim_data.get("name", "unnamed")
            is_required = name in REQUIRED_ANIMATIONS
            card_data = {
                "name": name,
                "spriteDirectionLeft": anim_data.get("sprite-direction-left", 0),
                "spriteDirectionTop": anim_data.get("sprite-direction-top", 0),
                "spriteDirectionWidth": anim_data.get("sprite-direction-width", 96),
                "spriteDirectionHeight": anim_data.get("sprite-direction-height", 96),
                "spriteLimit": anim_data.get("sprite-limit", 288),
                "spriteRange": anim_data.get("sprite-range", 96),
                "animated": anim_data.get("animated", True),
                "reverseMode": anim_data.get("reverse-mode", False),
                "loop": anim_data.get("loop", True),
                "sideFlip": anim_data.get("side-flip", True),
                "speed": anim_data.get("speed", 0.25),
                "sound": anim_data.get("sound", ""),
            }
            card = AnimationCard(len(self.animations), card_data, is_required)
            card.changed.connect(self._update_json_preview)
            card.removed.connect(self._remove_animation)
            self.animations_layout.addWidget(card)
            self.animations.append(card)

        self._update_json_preview()

    def _save_file(self):
        """Save JSON to file."""
        data = self._build_json()

        # Validate
        if not data.get("texturename"):
            QMessageBox.warning(self, "Validation Error", "The 'texturename' field is required.")
            return
        if not any(c.name_input.text().strip() == "stand" for c in self.animations):
            QMessageBox.warning(self, "Validation Error", "You need at least one animation with name 'stand'.")
            return

        filename = data.get("texturename", "sprite").replace("/", "_").replace("\\", "_") + ".json"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", filename, "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def _copy_json(self):
        """Copy JSON to clipboard."""
        data = self._build_json()
        json_str = json.dumps(data, indent=4)
        clipboard = QApplication.clipboard()
        clipboard.setText(json_str)
