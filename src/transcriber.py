from faster_whisper import WhisperModel
import numpy as np

class Transcriber:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        """
        Initializes the faster-whisper model.
        model_size: "tiny", "base", "small", "medium", "large-v3"
        device: "cpu" or "cuda"
        compute_type: "int8" or "float16" (if using cuda)
        
        Using 'tiny' or 'base' with int8 is highly recommended for speed on CPU.
        """
        print(f"Loading Whisper model '{model_size}'...", flush=True)
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Model loaded. Running warmup...", flush=True)
        self._warmup()

    def _warmup(self):
        """Runs a dummy inference to load the model fully into memory and cache."""
        try:
            # 1 second of silent audio (16kHz, float32)
            dummy_audio = np.zeros(16000, dtype=np.float32)
            list(self.model.transcribe(dummy_audio, beam_size=1))
            print("Warmup complete.", flush=True)
        except Exception as e:
            print(f"Warmup failed (ignoring): {e}")

    def transcribe(self, audio_data):
        """
        Transcribes the given audio data (numpy 1D array) and returns the text.
        """
        if audio_data is None or len(audio_data) == 0:
            print("No audio data provided.")
            return ""
            
        print("Transcribing...", flush=True)
        
        # vad_filter=True ignores silence to speed up processing
        # Lower beam_size (e.g., 2) for faster inference
        segments, info = self.model.transcribe(
            audio_data, 
            beam_size=2,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
            
        return full_text.strip()
