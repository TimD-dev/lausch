"""System tray icon with context menu."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication

    from lausch.settings import Settings

logger = logging.getLogger(__name__)


def _create_icon() -> QIcon:
    """Generate a simple 'L' icon matching the app style."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#E07A5F"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor("#F4EFE6"))
    painter.setFont(QFont("Times New Roman", 38, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), 0x0084, "L")  # AlignCenter
    painter.end()

    return QIcon(pixmap)


class LauschTray(QSystemTrayIcon):
    def __init__(
        self,
        app: QApplication,
        settings: Settings,
        on_settings: object,
        on_quit: object,
    ) -> None:
        super().__init__(_create_icon(), app)
        self.setToolTip("Lausch \u2014 Speech to Text")

        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #F4EFE6;
                border: 1px solid #E5E0D8;
                border-radius: 6px;
                padding: 4px;
                font-family: "Times New Roman";
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #3D3D3D;
            }
            QMenu::item:selected {
                background-color: #E07A5F;
                color: white;
                border-radius: 4px;
            }
            """
        )

        settings_action = QAction("Einstellungen", self)
        settings_action.triggered.connect(on_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction("Beenden", self)
        quit_action.triggered.connect(on_quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double-click on tray icon opens settings
            if self.contextMenu():
                actions = self.contextMenu().actions()
                if actions:
                    actions[0].trigger()
