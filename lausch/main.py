"""Main application orchestrator for Lausch."""

from __future__ import annotations

import logging
import sys
import threading
import time
from typing import TYPE_CHECKING

import keyboard

from lausch.audio.recorder import AudioRecorder
from lausch.input.text_inserter import TextInserter
from lausch.logging_setup import setup_logging
from lausch.settings import Settings
from lausch.transcription.transcriber import Transcriber

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QApplication

    from lausch.config import AppConfig

logger = logging.getLogger(__name__)


class LauschApp:
    def __init__(
        self,
        app: QApplication,
        transcriber: Transcriber,
        settings: Settings,
        config: AppConfig,
    ) -> None:
        from PyQt6.QtCore import QObject, pyqtSignal

        logger.info("Initializing application")
        self.app = app
        self.settings = settings
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
        self.recorder.on_audio_data = self.signals.update_audio.emit

        self.inserter = TextInserter(config.insertion)

        self.is_running = True
        self.recording_active = False

        # System tray
        from lausch.ui.tray import LauschTray

        self.tray = LauschTray(
            app,
            settings,
            on_settings=self._open_settings,
            on_quit=self._quit,
        )
        self.tray.show()

        self._settings_window = None

    def _open_settings(self) -> None:
        from lausch.ui.settings_window import SettingsWindow

        if self._settings_window is not None:
            self._settings_window.raise_()
            self._settings_window.activateWindow()
            return

        self._settings_window = SettingsWindow(self.settings)
        self._settings_window.settings_saved.connect(self._on_settings_saved)
        self._settings_window.destroyed.connect(
            lambda: setattr(self, "_settings_window", None)
        )
        from PyQt6.QtCore import Qt as QtCore_Qt

        self._settings_window.setAttribute(
            QtCore_Qt.WidgetAttribute.WA_DeleteOnClose
        )
        self._settings_window.show()

    def _on_settings_saved(self) -> None:
        logger.info("Settings changed, restart required for some changes")
        self.tray.showMessage(
            "Lausch",
            "Einstellungen gespeichert. Einige \u00c4nderungen werden beim n\u00e4chsten Start wirksam.",
            self.tray.MessageIcon.Information,
            3000,
        )

    def _quit(self) -> None:
        self.is_running = False
        if self.recording_active:
            self.recorder.stop_recording()
        self.app.quit()

    def toggle_recording(self) -> None:
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
        was_pressed = False
        while self.is_running:
            try:
                if keyboard.is_pressed(self.config.keyboard.exit_shortcut):
                    logger.info("Exiting application")
                    self._quit()
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
        settings = Settings()
        config = settings.to_app_config()

        # Load Transcriber BEFORE QApplication to avoid ctranslate2/PyQt6
        # OpenGL conflict that causes a segfault on Windows
        transcriber = Transcriber(config.transcriber)

        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication(sys.argv)
        lausch = LauschApp(app_instance, transcriber, settings, config)
        lausch.run()
    except KeyboardInterrupt:
        logger.info("App terminated by user")
        sys.exit(0)
