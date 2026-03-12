import keyboard
import time
import sys
import threading

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject

from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.text_inserter import TextInserter
from src.ui.overlay import OverlayWindow

class AppSignals(QObject):
    update_audio = pyqtSignal(list)
    show_ui = pyqtSignal()
    hide_ui = pyqtSignal()

class LauschApp:
    def __init__(self, app):
        print("Initializing Lausch App...", flush=True)
        self.app = app
        self.ui = OverlayWindow()
        self.signals = AppSignals()
        
        # Connect signals to UI (thread-safe UI updates)
        self.signals.update_audio.connect(self.ui.visualizer.update_amplitudes)
        self.signals.show_ui.connect(self.ui.show)
        self.signals.hide_ui.connect(self.ui.hide)

        self.recorder = AudioRecorder()
        # Wire the audio recording data right back to the Qt signal to animate the UI
        self.recorder.on_audio_data = self.signals.update_audio.emit
        
        self.transcriber = Transcriber() # This might take a few seconds to load the model
        self.inserter = TextInserter()
        
        self.is_running = True
        self.recording_active = False

    def toggle_recording(self):
        """Called when the shortcut is pressed in the background thread."""
        if not self.recording_active:
            print("\n--- [RECORDING STARTED] Speak now! ---", flush=True)
            self.recording_active = True
            
            # Show UI overlay via signal
            self.signals.show_ui.emit()
            
            self.recorder.start_recording()
        else:
            print("\n--- [RECORDING STOPPED] Processing... ---", flush=True)
            self.recording_active = False
            
            # Hide UI overlay via signal
            self.signals.hide_ui.emit()
            
            # 1. Stop recording and get numpy array audio data
            audio_data = self.recorder.stop_recording()
            
            if audio_data is not None:
                # 2. Transcribe
                text = self.transcriber.transcribe(audio_data)
                print(f"Recognized Text: {text}", flush=True)
                
                # 3. Insert Text
                time.sleep(0.2)
                self.inserter.insert_text(text)

    def _poll_shortcut(self, shortcut):
        """Polls for the shortcut in a background thread."""
        was_pressed = False
        while self.is_running:
            try:
                # Polling for 'esc' to gracefully close the application
                if keyboard.is_pressed('esc'):
                    print("Exiting Lausch App...", flush=True)
                    self.is_running = False
                    if self.recording_active:
                        self.recorder.stop_recording()
                    self.app.quit() # Tell PyQt6 event loop to quit
                    break

                is_pressed = keyboard.is_pressed(shortcut)
                if is_pressed and not was_pressed:
                    self.toggle_recording()
                was_pressed = is_pressed
                time.sleep(0.05) # Small sleep to prevent high CPU usage
            except Exception as e:
                print(f"Error polling keyboard: {e}")
                time.sleep(1)

    def run(self):
        shortcut = 'ctrl+space'
        print(f"\nLausch is ready! Press '{shortcut}' to start/stop dictating.", flush=True)
        print("Press 'esc' to exit the application completely.", flush=True)
        
        # Start the keyboard polling thread
        self.poll_thread = threading.Thread(target=self._poll_shortcut, args=(shortcut,), daemon=True)
        self.poll_thread.start()

        # Execute PyQt6 main loop directly in the main thread
        # This keeps the application alive and handles UI rendering
        sys.exit(self.app.exec())

if __name__ == "__main__":
    try:
        app_instance = QApplication(sys.argv)
        lausch = LauschApp(app_instance)
        lausch.run()
    except KeyboardInterrupt:
        print("\nApp terminated by user.")
        sys.exit(0)
