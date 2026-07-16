"""
Sprite Fusion Tab — Drag, organize and merge sprite images.
Port of duq-sprite-fusion from web to PySide6.
"""

import os
from pathlib import Path
from PIL import Image

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QFileDialog, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QColor, QDrag, QCursor


def pil_to_pixmap(img: Image.Image) -> QPixmap:
    """Convert a PIL Image to QPixmap."""
    if img.mode == "RGBA":
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    else:
        img = img.convert("RGB")
        data = img.tobytes("raw", "RGB")
        qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


class DraggableListWidget(QListWidget):
    """Custom list widget that supports drag-and-drop reordering."""

    order_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSpacing(6)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_changed.emit()


class SpriteFusionWidget(QWidget):
    """Main Sprite Fusion widget with drag-drop, preview, and export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data = []  # List of (path, PIL.Image, name, size)
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

        add_btn = QPushButton("📂 Add Images")
        add_btn.clicked.connect(self._add_images)
        toolbar_layout.addWidget(add_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self._clear_all)
        toolbar_layout.addWidget(clear_btn)

        toolbar_layout.addStretch()

        self.count_label = QLabel("0 images")
        self.count_label.setStyleSheet("color: #8b90a5; font-size: 12px;")
        toolbar_layout.addWidget(self.count_label)

        save_btn = QPushButton("💾 Export PNG")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._export_png)
        toolbar_layout.addWidget(save_btn)

        title = QLabel("🔀 Sprite Fusion")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #5b7aff;")
        toolbar_layout.addWidget(title)

        layout.addWidget(toolbar)

        # Main content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left: Image list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        list_header = QLabel("Sprite List")
        list_header.setStyleSheet("font-size: 12px; font-weight: 600; color: #8b90a5; text-transform: uppercase; letter-spacing: 0.5px;")
        left_layout.addWidget(list_header)

        # Drop zone
        self.drop_frame = QFrame()
        self.drop_frame.setObjectName("dropZone")
        self.drop_frame.setMinimumHeight(120)
        self.drop_frame.setAcceptDrops(True)
        self.drop_frame.dragEnterEvent = self._drag_enter
        self.drop_frame.dragLeaveEvent = self._drag_leave
        self.drop_frame.dropEvent = self._drop_event
        self.drop_frame.mousePressEvent = lambda e: self._add_images()
        drop_layout = QVBoxLayout(self.drop_frame)
        drop_layout.setAlignment(Qt.AlignCenter)

        drop_icon = QLabel("📁")
        drop_icon.setFont(QFont("Segoe UI Emoji", 32))
        drop_icon.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_icon)

        drop_text = QLabel("Drop PNG images here\nor click to browse")
        drop_text.setAlignment(Qt.AlignCenter)
        drop_text.setStyleSheet("color: #565b73; font-size: 13px;")
        drop_layout.addWidget(drop_text)

        left_layout.addWidget(self.drop_frame)

        # Image list
        self.image_list = DraggableListWidget()
        self.image_list.order_changed.connect(self._on_order_changed)
        self.image_list.setDragDropMode(QAbstractItemView.InternalMove)
        left_layout.addWidget(self.image_list)

        # Remove button
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.remove_btn.setEnabled(False)
        left_layout.addWidget(self.remove_btn)

        content_layout.addWidget(left_panel, 1)

        # Right: Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(8)

        preview_header = QHBoxLayout()
        preview_title = QLabel("Live Preview")
        preview_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #8b90a5; text-transform: uppercase; letter-spacing: 0.5px;")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()

        self.dim_label = QLabel("")
        self.dim_label.setStyleSheet("font-size: 11px; color: #565b73; font-family: monospace;")
        preview_header.addWidget(self.dim_label)
        right_layout.addLayout(preview_header)

        # Preview area
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1c2030;
                border: 1px solid #2a2f45;
                border-radius: 8px;
            }
        """)

        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: #565b73; font-size: 13px; padding: 40px;")
        self.preview_scroll.setWidget(self.preview_label)
        right_layout.addWidget(self.preview_scroll)

        content_layout.addWidget(right_panel, 1)

        layout.addWidget(content)

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_frame.setStyleSheet("""
                QFrame#dropZone {
                    background-color: rgba(91, 122, 255, 0.08);
                    border: 2px dashed #5b7aff;
                    border-radius: 12px;
                }
            """)

    def _drag_leave(self, event):
        self.drop_frame.setStyleSheet("")

    def _drop_event(self, event):
        self.drop_frame.setStyleSheet("")
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                self._load_image(path)

    def _add_images(self):
        """Open file dialog to add images."""
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files", "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)"
        )
        for path in paths:
            self._load_image(path)

    def _load_image(self, path: str):
        """Load an image file and add it to the list."""
        try:
            img = Image.open(path)
            name = os.path.basename(path)
            size = os.path.getsize(path)
            self.image_data.append((path, img, name, size))

            # Add to list widget
            item = QListWidgetItem(f"  {name}  ({img.width}×{img.height})  {format_file_size(size)}")
            item.setData(Qt.UserRole, len(self.image_data) - 1)
            self.image_list.addItem(item)

            self._update_ui()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load image:\n{e}")

    def _remove_selected(self):
        """Remove the selected image."""
        row = self.image_list.currentRow()
        if row >= 0:
            item = self.image_list.item(row)
            idx = item.data(Qt.UserRole)
            self.image_list.takeItem(row)
            if 0 <= idx < len(self.image_data):
                self.image_data.pop(idx)
            self._reindex()
            self._update_ui()

    def _clear_all(self):
        """Clear all images."""
        self.image_data.clear()
        self.image_list.clear()
        self._update_ui()

    def _reindex(self):
        """Re-index all items in the list."""
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            item.setData(Qt.UserRole, i)

    def _on_order_changed(self):
        """Handle drag-drop reorder."""
        new_order = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            idx = item.data(Qt.UserRole)
            if 0 <= idx < len(self.image_data):
                new_order.append(self.image_data[idx])
        self.image_data = new_order
        self._reindex()
        self._update_ui()

    def _update_ui(self):
        """Update UI state based on current data."""
        count = len(self.image_data)
        self.count_label.setText(f"{count} image{'s' if count != 1 else ''}")
        self.remove_btn.setEnabled(self.image_list.currentRow() >= 0)
        self._update_preview()

    def _update_preview(self):
        """Update the fused sprite preview."""
        if not self.image_data:
            self.preview_label.setText("Preview will appear here")
            self.preview_label.setStyleSheet("color: #565b73; font-size: 13px; padding: 40px;")
            self.dim_label.setText("")
            return

        try:
            # Calculate dimensions
            max_width = max(img.width for _, img, _, _ in self.image_data)
            total_height = sum(img.height for _, img, _, _ in self.image_data)

            self.dim_label.setText(f"{max_width} × {total_height} px")

            # Create fused image
            fused = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))
            y_offset = 0
            for _, img, _, _ in self.image_data:
                fused.paste(img, (0, y_offset))
                y_offset += img.height

            # Convert to pixmap
            pixmap = pil_to_pixmap(fused)

            # Scale to fit preview area
            preview_width = self.preview_scroll.viewport().width() - 20
            if preview_width <= 0:
                preview_width = 600  # fallback width
            if pixmap.width() > preview_width:
                pixmap = pixmap.scaledToWidth(preview_width, Qt.SmoothTransformation)

            self.preview_label.setPixmap(pixmap)
            self.preview_label.setStyleSheet("padding: 8px;")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {e}")
            self.preview_label.setStyleSheet("color: #ff4d6a; font-size: 13px; padding: 40px;")

    def _export_png(self):
        """Export the fused sprite as PNG."""
        if not self.image_data:
            QMessageBox.warning(self, "No Images", "Add at least one image before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Sprite Sheet", "duq-sprite-fusion.png",
            "PNG Files (*.png);;All Files (*)"
        )
        if not path:
            return

        try:
            max_width = max(img.width for _, img, _, _ in self.image_data)
            total_height = sum(img.height for _, img, _, _ in self.image_data)

            fused = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))
            y_offset = 0
            for _, img, _, _ in self.image_data:
                fused.paste(img, (0, y_offset))
                y_offset += img.height

            fused.save(path, "PNG")
            QMessageBox.information(self, "Exported", f"Sprite sheet saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")
