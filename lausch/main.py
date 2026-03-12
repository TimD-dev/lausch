"""Main application orchestrator for Lausch."""

from __future__ import annotations

import logging
import sys
import threading
import time
from typing import TYPE_CHECKING

import keyboard

from lausch.audio.recorder import AudioRecorder
from lausch.config import AppConfig
from lausch.input.text_inserter import TextInserter
from lausch.logging_setup import setup_logging
from lausch.transcription.transcriber import Transcriber

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


class LauschApp:
    def __init__(
        self,
        app: QApplication,
        transcriber: Transcriber,
        config: AppConfig = AppConfig(),
    ) -> None:
        from PyQt6.QtCore import QObject, pyqtSignal

        logger.info("Initializing application")
        self.app = app
        self.config = config

        self.transcriber = transcriber

        from lausch.ui.overlay import OverlayWindow

        self.ui = OverlayWindow(config.ui)

        # AppSignals must be defined after QApplication exists
        class AppSignals(QObject):
            update_audio = pyqtSignal(list)
            show_ui = pyqtSignal()
            hide_ui = pyqtSignal()

        self.signals = AppSignals()

        # Connect signals to UI (thread-safe UI updates)
        self.signals.update_audio.connect(self.ui.visualizer.update_amplitudes)
        self.signals.show_ui.connect(self.ui.show)
        self.signals.hide_ui.connect(self.ui.hide)

        self.recorder = AudioRecorder(config.audio)
        # Wire the audio recording data to the Qt signal to animate the UI
        self.recorder.on_audio_data = self.signals.update_audio.emit

        self.inserter = TextInserter(config.insertion)

        self.is_running = True
        self.recording_active = False

    def toggle_recording(self) -> None:
        """Called when the shortcut is pressed in the background thread."""
        if not self.recording_active:
            logger.info("Recording started")
            self.recording_active = True
            self.signals.show_ui.emit()
            self.recorder.start_recording()
        else:
            logger.info("Recording stopped, processing")
            self.recording_active = False
            self.signals.hide_ui.emit()

            audio_data = self.recorder.stop_recording()

            if audio_data is not None:
                text = self.transcriber.transcribe(audio_data)
                logger.info("Recognized text: %s", text)

                time.sleep(self.config.insertion.delay_before_paste)
                self.inserter.insert_text(text)

    def _poll_shortcut(self) -> None:
        """Poll for keyboard shortcuts in a background thread."""
        was_pressed = False
        while self.is_running:
            try:
                if keyboard.is_pressed(self.config.keyboard.exit_shortcut):
                    logger.info("Exiting application")
                    self.is_running = False
                    if self.recording_active:
                        self.recorder.stop_recording()
                    self.app.quit()
                    break

                is_pressed = keyboard.is_pressed(
                    self.config.keyboard.toggle_shortcut
                )
                if is_pressed and not was_pressed:
                    self.toggle_recording()
                was_pressed = is_pressed
                time.sleep(self.config.keyboard.poll_interval)
            except Exception:
                logger.error("Keyboard polling error", exc_info=True)
                time.sleep(self.config.keyboard.error_retry_delay)

    def run(self) -> None:
        logger.info(
            "Lausch is ready! Press '%s' to start/stop dictating.",
            self.config.keyboard.toggle_shortcut,
        )
        logger.info(
            "Press '%s' to exit the application.",
            self.config.keyboard.exit_shortcut,
        )

        self.poll_thread = threading.Thread(
            target=self._poll_shortcut, daemon=True
        )
        self.poll_thread.start()

        sys.exit(self.app.exec())


def main() -> None:
    setup_logging()
    try:
        config = AppConfig()

        # Load Transcriber BEFORE QApplication to avoid ctranslate2/PyQt6
        # OpenGL conflict that causes a segfault on Windows
        transcriber = Transcriber(config.transcriber)

        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication(sys.argv)
        lausch = LauschApp(app_instance, transcriber, config)
        lausch.run()
    except KeyboardInterrupt:
        logger.info("App terminated by user")
        sys.exit(0)
