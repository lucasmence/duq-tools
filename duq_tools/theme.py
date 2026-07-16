"""
Dark theme stylesheet for duq-tools.
Unified dark theme inspired by the original web tools.
"""

DARK_THEME = """
/* ═══════════════════════════════════════════════════════════════
   DUQ-TOOLS DARK THEME
   Unified dark theme for all tabs
   ═══════════════════════════════════════════════════════════════ */

/* ─── Global ─────────────────────────────────────────────── */
QWidget {
    background-color: #0f1117;
    color: #e2e4ed;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

/* ─── Main Window ────────────────────────────────────────── */
QMainWindow {
    background-color: #0f1117;
}

/* ─── Tab Widget ─────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2a2f45;
    background-color: #0f1117;
    border-radius: 0px;
}

QTabBar::tab {
    background-color: #161922;
    color: #8b90a5;
    border: 1px solid #2a2f45;
    border-bottom: none;
    padding: 10px 24px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #0f1117;
    color: #5b7aff;
    border-bottom: 2px solid #5b7aff;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #1c2030;
    color: #e2e4ed;
}

/* ─── Buttons ────────────────────────────────────────────── */
QPushButton {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #232840;
    border-color: #3a3f55;
}

QPushButton:pressed {
    background-color: #2a2f45;
}

QPushButton:disabled {
    background-color: #161922;
    color: #565b73;
    border-color: #1e2235;
}

QPushButton#primaryBtn,
QPushButton[class="primary"] {
    background-color: #5b7aff;
    color: #ffffff;
    border: none;
    font-weight: 600;
}

QPushButton#primaryBtn:hover,
QPushButton[class="primary"]:hover {
    background-color: #7b94ff;
}

QPushButton#dangerBtn,
QPushButton[class="danger"] {
    background-color: transparent;
    color: #ff4d6a;
    border: 1px solid #ff4d6a;
}

QPushButton#dangerBtn:hover,
QPushButton[class="danger"]:hover {
    background-color: rgba(255, 77, 106, 0.15);
}

/* ─── Input Fields ───────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #0f1117;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    selection-background-color: rgba(91, 122, 255, 0.3);
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #5b7aff;
    box-shadow: 0 0 0 3px rgba(91, 122, 255, 0.1);
}

QLineEdit::placeholder {
    color: #565b73;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #2a2f45;
    border-bottom: 1px solid #2a2f45;
    border-top-right-radius: 6px;
    background-color: #1c2030;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid #2a2f45;
    border-top: 1px solid #2a2f45;
    border-bottom-right-radius: 6px;
    background-color: #1c2030;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 8px;
    height: 8px;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 8px;
    height: 8px;
}

/* ─── Text Edit / Plain Text Edit ────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #1b1c18;
    color: #f8f8f2;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas", monospace;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: rgba(249, 38, 114, 0.3);
}

QPlainTextEdit {
    background-color: #1b1c18;
    color: #f8f8f2;
}

/* ─── Scroll Bars ────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #161922;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #2a2f45;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3a3f55;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #161922;
    height: 10px;
    margin: 0;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #2a2f45;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3a3f55;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* ─── Labels ─────────────────────────────────────────────── */
QLabel {
    color: #e2e4ed;
    background: transparent;
}

QLabel#sectionTitle {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #8b90a5;
}

QLabel#fieldLabel {
    font-size: 12px;
    font-weight: 500;
    color: #8b90a5;
}

/* ─── Combo Box ──────────────────────────────────────────── */
QComboBox {
    background-color: #0f1117;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #3a3f55;
}

QComboBox::drop-down {
    border-left: 1px solid #2a2f45;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    selection-background-color: #5b7aff;
    selection-color: #ffffff;
    padding: 4px;
}

/* ─── Check Box ──────────────────────────────────────────── */
QCheckBox {
    color: #8b90a5;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #2a2f45;
    background-color: #0f1117;
}

QCheckBox::indicator:checked {
    background-color: #5b7aff;
    border-color: #5b7aff;
}

QCheckBox::indicator:hover {
    border-color: #5b7aff;
}

/* ─── Group Box ──────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #2a2f45;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #e2e4ed;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    background-color: #0f1117;
}

/* ─── Splitter ───────────────────────────────────────────── */
QSplitter::handle {
    background-color: #2a2f45;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #5b7aff;
}

/* ─── Menu Bar ───────────────────────────────────────────── */
QMenuBar {
    background-color: #161922;
    color: #e2e4ed;
    border-bottom: 1px solid #2a2f45;
}

QMenuBar::item:selected {
    background-color: #232840;
}

QMenu {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #5b7aff;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #2a2f45;
    margin: 4px 8px;
}

/* ─── Tool Tip ───────────────────────────────────────────── */
QToolTip {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ─── Status Bar ─────────────────────────────────────────── */
QStatusBar {
    background-color: #161922;
    color: #8b90a5;
    border-top: 1px solid #2a2f45;
    font-size: 12px;
}

/* ─── Splash Screen ──────────────────────────────────────── */
QSplashScreen {
    background-color: #0f1117;
}

/* ─── File Dialog ────────────────────────────────────────── */
QFileDialog {
    background-color: #0f1117;
}

/* ─── List Widget ────────────────────────────────────────── */
QListWidget {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #2a2f45;
}

QListWidget::item:selected {
    background-color: rgba(91, 122, 255, 0.15);
    color: #5b7aff;
}

QListWidget::item:hover {
    background-color: #232840;
}

/* ─── Progress Bar ───────────────────────────────────────── */
QProgressBar {
    background-color: #1c2030;
    border: 1px solid #2a2f45;
    border-radius: 6px;
    text-align: center;
    color: #e2e4ed;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #5b7aff;
    border-radius: 5px;
}

/* ─── Slider ─────────────────────────────────────────────── */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #2a2f45;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #5b7aff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #7b94ff;
}

QSlider::sub-page:horizontal {
    background: #5b7aff;
    border-radius: 3px;
}

/* ─── Sprite Editor Specific ─────────────────────────────── */
QFrame#spritePanel {
    background-color: #161922;
    border: 1px solid #2a2f45;
    border-radius: 8px;
}

/* ─── Trigger Editor Specific ────────────────────────────── */
QPlainTextEdit#codeEditor {
    background-color: #1b1c18;
    color: #f8f8f2;
    font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", monospace;
    font-size: 14px;
    line-height: 1.6;
    border: none;
    padding: 8px 12px;
}

/* ─── Animation Card ─────────────────────────────────────── */
QFrame#animationCard {
    background-color: #1c2030;
    border: 1px solid #2a2f45;
    border-radius: 8px;
}

QFrame#animationCard:hover {
    border-color: #3a3f55;
}

/* ─── JSON Preview ───────────────────────────────────────── */
QTextBrowser#jsonPreview {
    background-color: #1c2030;
    color: #e2e4ed;
    border: 1px solid #2a2f45;
    border-radius: 8px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
    padding: 12px;
}

/* ─── Image List (Fusion) ────────────────────────────────── */
QFrame#imageCard {
    background-color: #1c2030;
    border: 1px solid #2a2f45;
    border-radius: 8px;
    padding: 8px;
}

QFrame#imageCard:hover {
    background-color: #232840;
    border-color: #3a3f55;
}

/* ─── Drop Zone ──────────────────────────────────────────── */
QFrame#dropZone {
    background-color: #161922;
    border: 2px dashed #3a3f55;
    border-radius: 12px;
}

QFrame#dropZone:hover {
    border-color: #5b7aff;
    background-color: rgba(91, 122, 255, 0.05);
}

/* ─── Preview Canvas ─────────────────────────────────────── */
QLabel#previewCanvas {
    background-color: #0f1117;
    border: 1px solid #2a2f45;
    border-radius: 8px;
}

/* ─── Validation Badge ───────────────────────────────────── */
QLabel#validationBadge {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 500;
}

QLabel#validationBadge[valid="true"] {
    background-color: rgba(52, 211, 153, 0.12);
    color: #34d399;
}

QLabel#validationBadge[valid="false"] {
    background-color: rgba(255, 77, 106, 0.12);
    color: #ff4d6a;
}

/* ─── Notification Toast ─────────────────────────────────── */
QFrame#notification {
    background-color: #1c2030;
    border: 1px solid #2a2f45;
    border-radius: 8px;
    padding: 12px 16px;
}

QFrame#notification[type="error"] {
    border-color: rgba(255, 77, 106, 0.4);
    background-color: rgba(255, 77, 106, 0.1);
}

QFrame#notification[type="success"] {
    border-color: rgba(52, 211, 153, 0.4);
    background-color: rgba(52, 211, 153, 0.1);
}

"""
