"""Clipboard-based text insertion at the current cursor position."""

from __future__ import annotations

import logging
import time

import keyboard
import pyperclip

from lausch.config import InsertionConfig

logger = logging.getLogger(__name__)


class TextInserter:
    def __init__(self, config: InsertionConfig = InsertionConfig()) -> None:
        self.config = config

    def insert_text(self, text: str) -> None:
        """
        Insert text at the current cursor position by:
        1. Backing up the current clipboard.
        2. Setting clipboard to the transcribed text.
        3. Firing Ctrl+V.
        4. Restoring the original clipboard.
        """
        if not text:
            return

        logger.debug("Inserting text: %s", text[:50])

        original_clipboard = pyperclip.paste()

        try:
            pyperclip.copy(text)
            keyboard.send("ctrl+v")
            time.sleep(self.config.delay_after_paste)
        except Exception:
            logger.error("Text insertion error", exc_info=True)
        finally:
            pyperclip.copy(original_clipboard)
            logger.debug("Text inserted, clipboard restored")
