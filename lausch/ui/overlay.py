"""Borderless PyQt6 desktop overlay window."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

from lausch.config import UIConfig
from lausch.ui.visualizer import AudioVisualizerWidget


class OverlayWindow(QWidget):
    def __init__(self, config: UIConfig = UIConfig()) -> None:
        super().__init__()
        self.config = config

        # Frameless, always on top, not shown in taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        # Transparent background so we can draw rounded corners in paintEvent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QHBoxLayout(self)
        m = config.layout_margins
        layout.setContentsMargins(m[0], m[1], m[2], m[3])
        layout.setSpacing(config.layout_spacing)

        # Logo label
        self.logo_label = QLabel("L")
        font = QFont(config.logo_font_family, config.logo_font_size, QFont.Weight.Bold)
        self.logo_label.setFont(font)
        self.logo_label.setStyleSheet(
            f"color: {config.color_accent};"
        )
        layout.addWidget(self.logo_label)

        # Audio visualizer
        self.visualizer = AudioVisualizerWidget(config)
        layout.addWidget(self.visualizer)

        # Set geometry after layout is calculated
        QTimer.singleShot(0, self.setup_geometry)

    def setup_geometry(self) -> None:
        self.resize(self.config.window_width, self.config.window_height)
        self.center_at_bottom()

    def center_at_bottom(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        if self.config.position == "top":
            y = self.config.taskbar_offset
        else:
            y = screen.height() - self.height() - self.config.taskbar_offset
        self.move(x, y)

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(self.config.color_background))

        pen = QPen(QColor(self.config.color_border))
        pen.setWidth(1)
        painter.setPen(pen)

        painter.drawRoundedRect(
            0,
            0,
            self.width() - 1,
            self.height() - 1,
            self.config.corner_radius,
            self.config.corner_radius,
        )
