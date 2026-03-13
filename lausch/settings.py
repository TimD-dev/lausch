"""JSON-based persistent settings for the Lausch application."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from lausch.config import (
    AppConfig,
    AudioConfig,
    InsertionConfig,
    KeyboardConfig,
    TranscriberConfig,
    UIConfig,
)

logger = logging.getLogger(__name__)

DEFAULTS = {
    "language": "auto",
    "model_size": "small",
    "shortcut": "ctrl+space",
    "microphone": None,
    "ui_position": "bottom",
    "autostart": False,
    "volume_boost": 50.0,
}

# Context prompts that condition Whisper for better recognition per language.
# These prime the decoder with proper punctuation, capitalization, and style.
_INITIAL_PROMPTS: dict[str | None, str] = {
    "de": (
        "Hallo, dies ist eine Aufnahme auf Deutsch. "
        "Bitte transkribiere den folgenden Text mit korrekter Groß- und Kleinschreibung "
        "und Zeichensetzung."
    ),
    "en": (
        "Hello, this is a recording in English. "
        "Please transcribe the following text with proper capitalization and punctuation."
    ),
    None: (
        "This is a multilingual recording. "
        "Transcribe with proper punctuation and capitalization. "
        "Dies ist eine mehrsprachige Aufnahme."
    ),
}


class Settings:
    def __init__(self) -> None:
        appdata = os.environ.get("APPDATA", str(Path.home()))
        self.path = Path(appdata) / "Lausch" / "settings.json"
        self.data: dict = self._load()

    def _load(self) -> dict:
        defaults = dict(DEFAULTS)
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    saved = json.load(f)
                defaults.update(saved)
                logger.info("Settings loaded from %s", self.path)
            except Exception:
                logger.warning("Failed to load settings, using defaults", exc_info=True)
        return defaults

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        logger.info("Settings saved to %s", self.path)

    def get(self, key: str, default: object = None) -> object:
        return self.data.get(key, default)

    def set(self, key: str, value: object) -> None:
        self.data[key] = value

    def to_app_config(self) -> AppConfig:
        language = self.data["language"]
        if language == "auto":
            language = None

        # Pick the best initial_prompt for the selected language
        initial_prompt = _INITIAL_PROMPTS.get(
            language, _INITIAL_PROMPTS[None]
        )

        return AppConfig(
            audio=AudioConfig(
                volume_boost_factor=self.data["volume_boost"],
                device=self.data["microphone"],
            ),
            transcriber=TranscriberConfig(
                model_size=self.data["model_size"],
                language=language,
                initial_prompt=initial_prompt,
            ),
            ui=UIConfig(
                position=self.data["ui_position"],
            ),
            keyboard=KeyboardConfig(
                toggle_shortcut=self.data["shortcut"],
            ),
            insertion=InsertionConfig(),
        )
