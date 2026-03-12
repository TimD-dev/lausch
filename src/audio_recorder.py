import sounddevice as sd
import numpy as np
import threading
import queue

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self._thread = None
        self.recorded_frames = []
        self.on_audio_data = None # Optional callback for UI visualization

    def _audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, flush=True)
        if self.is_recording:
            self.audio_queue.put(indata.copy())
            
            if self.on_audio_data:
                # Calculate a simple RMS volume score (0.0 to ~1.0)
                rms = np.sqrt(np.mean(indata**2))
                # Boost it a bit for visual effect
                vol = min(1.0, rms * 15)
                # Generate a simple 10-bar pseudo visualization based on volume
                bars = [min(1.0, vol * (0.6 + 0.4 * np.random.rand())) for _ in range(10)]
                self.on_audio_data(bars)

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.audio_queue = queue.Queue() # Reset queue
        self.recorded_frames = []
        print("Recording started...")

        def record():
            try:
                with sd.InputStream(samplerate=self.sample_rate, channels=self.channels,
                                    callback=self._audio_callback):
                    while self.is_recording or not self.audio_queue.empty():
                        try:
                            # Use timeout so we can periodically check self.is_recording
                            data = self.audio_queue.get(timeout=0.1)
                            self.recorded_frames.append(data)
                        except queue.Empty:
                            continue
            except Exception as e:
                print(f"Error during audio recording: {e}")
                self.is_recording = False

        self._thread = threading.Thread(target=record)
        self._thread.start()

    def stop_recording(self):
        if not self.is_recording:
            return None
            
        self.is_recording = False
        if self._thread:
            self._thread.join()
        
        print("Recording stopped.")
        
        if not self.recorded_frames:
            return None
            
        # Concatenate chunks into a 1D float32 numpy array
        audio_data = np.concatenate(self.recorded_frames, axis=0)
        audio_data = audio_data.flatten().astype(np.float32)
        
        return audio_data

# Simple test block if run directly
if __name__ == "__main__":
    import time
    recorder = AudioRecorder()
    recorder.start_recording()
    time.sleep(3) # Record for 3 seconds
    audio_data = recorder.stop_recording()
    if audio_data is not None:
        print(f"Test recorded to numpy array of shape: {audio_data.shape}")
    else:
        print("No audio recorded.")
