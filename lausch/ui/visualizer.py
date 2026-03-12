"""Audio visualizer widget with animated bars."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from lausch.config import UIConfig


class AudioVisualizerWidget(QWidget):
    def __init__(
        self, config: UIConfig = UIConfig(), parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.setMinimumSize(config.visualizer_min_width, config.visualizer_min_height)
        self.amplitudes: list[float] = [config.min_amplitude] * 10

    @pyqtSlot(list)
    def update_amplitudes(self, data: list[float]) -> None:
        """Expects a list of float values between 0.0 and 1.0."""
        self.amplitudes = data
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        bar_width = width / len(self.amplitudes)
        spacing = self.config.bar_spacing

        painter.setBrush(QColor(self.config.color_accent))
        painter.setPen(Qt.PenStyle.NoPen)

        for i, amp in enumerate(self.amplitudes):
            amp = max(self.config.min_amplitude, min(1.0, amp))
            bar_h = height * amp
            x = i * bar_width + spacing / 2
            y = (height - bar_h) / 2  # Vertically centered

            painter.drawRoundedRect(
                int(x), int(y), int(bar_width - spacing), int(bar_h), 2, 2
            )
