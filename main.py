#!/usr/bin/env python3
"""
duq-tools — Unified desktop toolkit for 2D game development.
Combines Sprite Editor, Sprite Fusion, and Trigger Editor into one app.
"""

import sys
import os
import time
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QSplashScreen, QLabel,
    QVBoxLayout, QWidget, QHBoxLayout, QFrame, QDialog
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QLinearGradient, QAction

from datetime import datetime

APP_VERSION = "1.0.0"
APP_WEBSITE = "https://github.com/duqtools/duq-tools"

from duq_tools.theme import DARK_THEME
from duq_tools.sprite_editor import SpriteEditorWidget
from duq_tools.sprite_fusion import SpriteFusionWidget
from duq_tools.trigger_editor import TriggerEditorWidget


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class SplashScreen(QWidget):
    """Custom splash screen with animated loading bar."""

    def __init__(self, icon_path: str):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(420, 320)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        # Icon
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            icon_label.setText("🎮")
            icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("duq-tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #5b7aff; letter-spacing: -0.5px;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Sprite Editor • Sprite Fusion • Trigger Editor")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #8b90a5;")
        layout.addWidget(subtitle)

        # Loading bar container
        bar_container = QFrame()
        bar_container.setFixedHeight(6)
        bar_container.setStyleSheet("""
            QFrame {
                background-color: #2a2f45;
                border-radius: 3px;
            }
        """)
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        self.loading_bar = QFrame(bar_container)
        self.loading_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5b7aff, stop:1 #7b94ff);
                border-radius: 3px;
            }
        """)
        self.loading_bar.setFixedHeight(6)
        self.loading_bar.setFixedWidth(0)
        bar_layout.addWidget(self.loading_bar)

        layout.addWidget(bar_container)

        # Version
        version = QLabel(f"v{APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet("color: #565b73;")
        layout.addWidget(version)

        # Animate loading bar
        self._progress = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._advance)
        self._timer.start(16)  # ~60fps

    def _advance(self):
        self._progress += 1
        width = int(self._progress * 3.5)  # Fill in ~2.3 seconds
        if width > 380:
            width = 380
        self.loading_bar.setFixedWidth(width)
        if self._progress >= 110:
            self._timer.stop()


class AboutDialog(QDialog):
    """Styled About dialog for duq-tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About duq-tools")
        self.setFixedSize(480, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1117;
            }
            QLabel {
                color: #e2e4ed;
                background: transparent;
            }
            QPushButton {
                background-color: #5b7aff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #7b94ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel()
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            icon_label.setText("🎮")
            icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("duq-tools")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #5b7aff; letter-spacing: -0.5px;")
        layout.addWidget(title)

        # Version
        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Segoe UI", 11))
        version.setStyleSheet("color: #8b90a5;")
        layout.addWidget(version)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #2a2f45; max-height: 1px; margin: 8px 40px;")
        layout.addWidget(separator)

        # Description
        desc = QLabel(
            "A unified desktop toolkit for 2D game development.\n"
            "Combines Sprite Editor, Sprite Fusion, and Trigger Editor\n"
            "into a single application."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color: #8b90a5; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Features
        features = QLabel(
            "🎨  Sprite Editor — Create and edit 2D sprite textures\n"
            "🔀  Sprite Fusion  — Merge multiple sprite sheets\n"
            "⚡  Trigger Editor — Define map triggers and events"
        )
        features.setAlignment(Qt.AlignCenter)
        features.setFont(QFont("Segoe UI", 10))
        features.setStyleSheet("color: #565b73; line-height: 1.6; margin-top: 4px;")
        features.setWordWrap(True)
        layout.addWidget(features)

        layout.addStretch()

        # Copyright
        year = datetime.now().year
        copyright_label = QLabel(f"© {year} Duq. Built with PySide6 & Python.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Segoe UI", 9))
        copyright_label.setStyleSheet("color: #3a3f55; margin-top: 8px;")
        layout.addWidget(copyright_label)

        # Close button
        close_btn = QPushButton("OK")
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("duq-tools")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Set window icon
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        # Create tabs
        self.sprite_editor = SpriteEditorWidget()
        self.sprite_fusion = SpriteFusionWidget()
        self.trigger_editor = TriggerEditorWidget()

        # Add tabs with icons from each editor folder
        sprite_icon = QIcon(get_resource_path(os.path.join("duq-sprite-editor", "icon.png")))
        fusion_icon = QIcon(get_resource_path(os.path.join("duq-sprite-fusion", "icon.png")))
        trigger_icon = QIcon(get_resource_path(os.path.join("duq-trigger-editor", "icon.png")))

        self.tabs.addTab(self.sprite_editor, sprite_icon, "Sprite Editor")
        self.tabs.addTab(self.sprite_fusion, fusion_icon, "Sprite Fusion")
        self.tabs.addTab(self.trigger_editor, trigger_icon, "Trigger Editor")

        main_layout.addWidget(self.tabs)

        # Menu bar
        self._setup_menu_bar()

        # Status bar
        self.statusBar().showMessage("Ready")

        # Keyboard shortcuts
        self._setup_shortcuts()

    def _setup_menu_bar(self):
        """Create the menu bar with Help > About."""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #161922;
                color: #e2e4ed;
                border-bottom: 1px solid #2a2f45;
                padding: 2px 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
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
        """)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("About duq-tools", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        # Separator
        help_menu.addSeparator()

        # Website action
        website_action = QAction("Visit Website", self)
        website_action.triggered.connect(self._open_website)
        help_menu.addAction(website_action)

    def _show_about(self):
        """Show the About dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _open_website(self):
        """Open the project website."""
        import webbrowser
        webbrowser.open(APP_WEBSITE)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        from PySide6.QtGui import QShortcut, QKeySequence

        # Ctrl+Tab to switch tabs
        QShortcut(QKeySequence("Ctrl+Tab"), self, self._next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self._prev_tab)

    def _next_tab(self):
        idx = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((idx + 1) % self.tabs.count())

    def _prev_tab(self):
        idx = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((idx - 1) % self.tabs.count())


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Apply dark theme
    app.setStyleSheet(DARK_THEME)

    # Set application metadata
    app.setApplicationName("duq-tools")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Duq")

    # Get icon path
    icon_path = get_resource_path("icon.png")

    # Show splash screen
    splash = SplashScreen(icon_path)
    splash.show()
    app.processEvents()

    # Create main window (while splash is showing)
    window = MainWindow()

    # Close splash and show window after 2 seconds
    def show_main():
        splash.close()
        window.show()
        window.activateWindow()
        window.raise_()

    QTimer.singleShot(2200, show_main)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
