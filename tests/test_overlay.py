import sys
import os
import time
import wave
import threading
import numpy as np

from PyQt6.QtWidgets import QApplication
from lausch.ui.overlay import OverlayWindow


def audio_simulation_thread(overlay_window, wav_file_path):
    print("Background thread for audio simulation started.")

    if not os.path.exists(wav_file_path):
        print(f"Error: Audio file '{wav_file_path}' not found.")
        return

    wf = wave.open(wav_file_path, 'rb')
    sample_rate = wf.getframerate()
    chunk_size = 1024

    while True:
        data = wf.readframes(chunk_size)
        if not data:
            wf.rewind()
            continue

        samples = np.frombuffer(data, dtype=np.int16)

        bars = 10
        section_size = len(samples) // bars
        amplitudes = []

        for i in range(bars):
            start = i * section_size
            end = start + section_size
            section = samples[start:end]
            if len(section) > 0:
                rms = np.sqrt(np.mean(np.square(section, dtype=np.float64)))
                norm_amp = min(1.0, rms / 6000.0)
                amplitudes.append(norm_amp)
            else:
                amplitudes.append(0.0)

        overlay_window.visualizer.update_amplitudes(amplitudes)

        time.sleep(chunk_size / sample_rate)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OverlayWindow()
    window.show()

    test_wav = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_audio.wav')

    if not os.path.exists(test_wav):
        from tests.fixtures.generate_test_audio import generate_test_file
        generate_test_file(test_wav)

    thread = threading.Thread(target=audio_simulation_thread, args=(window, test_wav), daemon=True)
    thread.start()

    print("UI Overlay running. Close the window to exit.")
    exit_code = app.exec()
    print("Done.")
    sys.exit(exit_code)
