"""Settings window with Times New Roman aesthetic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import sounddevice as sd
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from lausch.settings import Settings

logger = logging.getLogger(__name__)

# Design constants matching the overlay
BG = "#F4EFE6"
ACCENT = "#E07A5F"
BORDER = "#E5E0D8"
TEXT = "#3D3D3D"
FONT_FAMILY = "Times New Roman"

LANGUAGES = [
    ("Auto-Erkennung", "auto"),
    ("Deutsch", "de"),
    ("English", "en"),
    ("Fran\u00e7ais", "fr"),
    ("Espa\u00f1ol", "es"),
]

MODELS = [
    ("Tiny \u2014 schnell, weniger genau", "tiny"),
    ("Base \u2014 gute Balance", "base"),
    ("Small \u2014 genauer, langsamer", "small"),
    ("Medium \u2014 sehr genau, langsam", "medium"),
]

STYLESHEET = f"""
    QWidget#SettingsWindow {{
        background-color: {BG};
    }}
    QLabel {{
        color: {TEXT};
        font-family: "{FONT_FAMILY}";
        font-size: 13px;
    }}
    QLabel#SectionLabel {{
        font-size: 15px;
        font-weight: bold;
        color: {ACCENT};
        font-family: "{FONT_FAMILY}";
        padding-top: 8px;
    }}
    QLabel#TitleLabel {{
        font-size: 22px;
        font-weight: bold;
        color: {ACCENT};
        font-family: "{FONT_FAMILY}";
    }}
    QComboBox, QLineEdit {{
        background-color: white;
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-family: "{FONT_FAMILY}";
        font-size: 13px;
        color: {TEXT};
    }}
    QComboBox:focus, QLineEdit:focus {{
        border: 1px solid {ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QSlider::groove:horizontal {{
        height: 6px;
        background: {BORDER};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {ACCENT};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {ACCENT};
        border-radius: 3px;
    }}
    QCheckBox {{
        font-family: "{FONT_FAMILY}";
        font-size: 13px;
        color: {TEXT};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {BORDER};
        border-radius: 4px;
        background: white;
    }}
    QCheckBox::indicator:checked {{
        background: {ACCENT};
        border-color: {ACCENT};
    }}
    QPushButton#SaveButton {{
        background-color: {ACCENT};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 28px;
        font-family: "{FONT_FAMILY}";
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton#SaveButton:hover {{
        background-color: #C96A50;
    }}
    QPushButton#CancelButton {{
        background-color: white;
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 28px;
        font-family: "{FONT_FAMILY}";
        font-size: 14px;
    }}
    QPushButton#CancelButton:hover {{
        background-color: {BORDER};
    }}
"""


class SettingsWindow(QWidget):
    settings_saved = pyqtSignal()

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.setObjectName("SettingsWindow")
        self.setWindowTitle("Lausch \u2014 Einstellungen")
        self.setFixedSize(420, 560)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(6)

        # Title
        title = QLabel("Lausch")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        layout.addSpacing(8)

        # --- Language ---
        layout.addWidget(self._section("Sprache"))
        self.language_combo = QComboBox()
        for label, value in LANGUAGES:
            self.language_combo.addItem(label, value)
        layout.addWidget(self.language_combo)

        # --- Model ---
        layout.addWidget(self._section("Modell"))
        self.model_combo = QComboBox()
        for label, value in MODELS:
            self.model_combo.addItem(label, value)
        layout.addWidget(self.model_combo)

        # --- Shortcut ---
        layout.addWidget(self._section("Shortcut"))
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setPlaceholderText("z.B. ctrl+space")
        layout.addWidget(self.shortcut_edit)

        # --- Microphone ---
        layout.addWidget(self._section("Mikrofon"))
        self.mic_combo = QComboBox()
        self._populate_microphones()
        layout.addWidget(self.mic_combo)

        # --- UI Position ---
        layout.addWidget(self._section("Overlay-Position"))
        self.position_combo = QComboBox()
        self.position_combo.addItem("Unten", "bottom")
        self.position_combo.addItem("Oben", "top")
        layout.addWidget(self.position_combo)

        # --- Volume Boost / Sensitivity ---
        layout.addWidget(self._section("Empfindlichkeit"))
        slider_row = QHBoxLayout()
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(10, 200)
        self.sensitivity_slider.setTickInterval(10)
        self.sensitivity_label = QLabel("50")
        self.sensitivity_label.setFixedWidth(30)
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(str(v))
        )
        slider_row.addWidget(self.sensitivity_slider)
        slider_row.addWidget(self.sensitivity_label)
        layout.addLayout(slider_row)

        # --- Autostart ---
        self.autostart_check = QCheckBox("Bei Windows-Start automatisch starten")
        layout.addWidget(self.autostart_check)

        layout.addStretch()

        # --- Buttons ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Speichern")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _section(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    def _populate_microphones(self) -> None:
        self.mic_combo.addItem("System-Standard", None)
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev["max_input_channels"] > 0:
                    self.mic_combo.addItem(dev["name"], i)
        except Exception:
            logger.warning("Could not query audio devices", exc_info=True)

    def _load_values(self) -> None:
        # Language
        lang = self.settings.data.get("language", "auto")
        idx = self.language_combo.findData(lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

        # Model
        model = self.settings.data.get("model_size", "base")
        idx = self.model_combo.findData(model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)

        # Shortcut
        self.shortcut_edit.setText(self.settings.data.get("shortcut", "ctrl+space"))

        # Microphone
        mic = self.settings.data.get("microphone")
        idx = self.mic_combo.findData(mic)
        if idx >= 0:
            self.mic_combo.setCurrentIndex(idx)

        # Position
        pos = self.settings.data.get("ui_position", "bottom")
        idx = self.position_combo.findData(pos)
        if idx >= 0:
            self.position_combo.setCurrentIndex(idx)

        # Sensitivity
        boost = int(self.settings.data.get("volume_boost", 50))
        self.sensitivity_slider.setValue(boost)

        # Autostart
        self.autostart_check.setChecked(self.settings.data.get("autostart", False))

    def _save(self) -> None:
        self.settings.data["language"] = self.language_combo.currentData()
        self.settings.data["model_size"] = self.model_combo.currentData()
        self.settings.data["shortcut"] = self.shortcut_edit.text().strip()
        self.settings.data["microphone"] = self.mic_combo.currentData()
        self.settings.data["ui_position"] = self.position_combo.currentData()
        self.settings.data["volume_boost"] = self.sensitivity_slider.value()
        self.settings.data["autostart"] = self.autostart_check.isChecked()
        self.settings.save()

        # Handle autostart
        from lausch.autostart import set_autostart
        set_autostart(self.settings.data["autostart"])

        self.settings_saved.emit()
        self.close()
        logger.info("Settings saved and applied")
