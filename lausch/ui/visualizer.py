"""Audio visualizer widget with smooth animated bars."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from lausch.config import UIConfig

# How fast bars move toward their target (0 = instant, 1 = frozen)
_SMOOTHING = 0.6
# How quickly bars decay back to idle when no new data arrives
_DECAY = 0.92
# Animation refresh rate in milliseconds
_FRAME_INTERVAL_MS = 30


class AudioVisualizerWidget(QWidget):
    def __init__(
        self, config: UIConfig = UIConfig(), parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.setMinimumSize(config.visualizer_min_width, config.visualizer_min_height)

        n = 10
        self._target: list[float] = [config.min_amplitude] * n
        self._current: list[float] = [config.min_amplitude] * n
        self.amplitudes: list[float] = [config.min_amplitude] * n

        # Smooth animation timer — runs at ~33fps
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(_FRAME_INTERVAL_MS)

    @pyqtSlot(list)
    def update_amplitudes(self, data: list[float]) -> None:
        """Set new target amplitudes. The bars will smoothly animate toward them."""
        self._target = data

    def _animate(self) -> None:
        """Interpolate current bars toward target, then repaint."""
        changed = False
        for i in range(len(self._current)):
            target = self._target[i] if i < len(self._target) else self.config.min_amplitude

            # Lerp toward target
            old = self._current[i]
            new = old * _SMOOTHING + target * (1.0 - _SMOOTHING)

            # Apply decay (bars slowly fall back to idle)
            if new < old:
                new = old * _DECAY

            new = max(self.config.min_amplitude, min(1.0, new))

            if abs(new - old) > 0.001:
                changed = True
            self._current[i] = new

        if changed:
            self.amplitudes = list(self._current)
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
