import sys
import os
import time
import wave
import threading
import numpy as np

# Den src Ordner in den Python-Pfad aufnehmen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication
from src.ui.overlay import OverlayWindow

def audio_simulation_thread(overlay_window, wav_file_path):
    print("Hintergrund-Thread für Audio-Simulation gestartet.")
    
    if not os.path.exists(wav_file_path):
        print(f"Fehler: Audio-Datei '{wav_file_path}' nicht gefunden.")
        return
        
    wf = wave.open(wav_file_path, 'rb')
    sample_rate = wf.getframerate()
    chunk_size = 1024
    
    while True:
        data = wf.readframes(chunk_size)
        if not data:
            # Datei von vorne beginnen
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
                # RMS (Root Mean Square) berechnen
                rms = np.sqrt(np.mean(np.square(section, dtype=np.float64)))
                # Normalisieren (anpassen je nach Lautstärke)
                norm_amp = min(1.0, rms / 6000.0) 
                amplitudes.append(norm_amp)
            else:
                amplitudes.append(0.0)
                
        # Signal an die GUI übergeben (thread-sicher)
        overlay_window.audio_update_signal.emit(amplitudes)
        
        # Pausieren, um reale Audio-Wiedergabe zu simulieren
        time.sleep(chunk_size / sample_rate)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = OverlayWindow()
    window.show()
    
    test_wav = os.path.join(os.path.dirname(__file__), '..', 'src', 'ui', 'test_audio.wav')
    
    if not os.path.exists(test_wav):
        from src.ui.test_audio_generator import generate_test_file
        generate_test_file(test_wav)
    
    # Daemon-Thread: bricht ab, wenn das Hauptprogramm (UI) geschlossen wird
    thread = threading.Thread(target=audio_simulation_thread, args=(window, test_wav), daemon=True)
    thread.start()
    
    print("UI Overlay läuft. Schließe das Fenster zum Beenden.")
    exit_code = app.exec()
    print("Beendet.")
    sys.exit(exit_code)
