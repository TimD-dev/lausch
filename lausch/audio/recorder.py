"""Microphone audio capture with threading and visualization support."""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, Callable

import numpy as np
import sounddevice as sd

from lausch.config import AudioConfig

logger = logging.getLogger(__name__)

# Target RMS level for audio normalization (0.1 = comfortable speech level)
_TARGET_RMS = 0.1
# Smoothing factor for adaptive gain (0 = no smoothing, 1 = fully smoothed)
_GAIN_SMOOTHING = 0.95
# Maximum gain to prevent amplifying silence/noise too much
_MAX_GAIN = 50.0
# Minimum gain to prevent clipping loud audio
_MIN_GAIN = 1.0


class AudioRecorder:
    def __init__(self, config: AudioConfig = AudioConfig()) -> None:
        self.config = config
        self.is_recording = False
        self.audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._thread: threading.Thread | None = None
        self.recorded_frames: list[np.ndarray] = []
        self.on_audio_data: Callable[[list[float]], None] | None = None
        # Adaptive gain for RMS normalization
        self._current_gain: float = 10.0

    def _compute_adaptive_gain(self, rms: float) -> float:
        """Compute adaptive gain to normalize audio to target RMS level."""
        if rms < 1e-7:
            # Silence — don't adjust gain
            return self._current_gain

        ideal_gain = _TARGET_RMS / rms
        ideal_gain = max(_MIN_GAIN, min(_MAX_GAIN, ideal_gain))

        # Smooth the gain to avoid sudden jumps
        self._current_gain = (
            _GAIN_SMOOTHING * self._current_gain
            + (1 - _GAIN_SMOOTHING) * ideal_gain
        )
        return self._current_gain

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: Any,
        status: sd.CallbackFlags,
    ) -> None:
        """Called from a separate thread for each audio block."""
        if status:
            logger.warning("Audio stream status: %s", status)
        if self.is_recording:
            self.audio_queue.put(indata.copy())

            if self.on_audio_data:
                rms = np.sqrt(np.mean(indata**2))
                self._compute_adaptive_gain(rms)

                # Use adaptive gain for visualizer (much more sensitive)
                vol = min(1.0, rms * self._current_gain * self.config.volume_boost_factor / 10.0)
                bars = [
                    min(1.0, vol * (0.6 + 0.4 * np.random.rand()))
                    for _ in range(self.config.visualizer_bar_count)
                ]
                self.on_audio_data(bars)

    def start_recording(self) -> None:
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_queue = queue.Queue()
        self.recorded_frames = []
        logger.debug("Recording stream opened")

        def record() -> None:
            try:
                with sd.InputStream(
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    device=self.config.device,
                    callback=self._audio_callback,
                ):
                    while self.is_recording or not self.audio_queue.empty():
                        try:
                            data = self.audio_queue.get(
                                timeout=self.config.queue_timeout
                            )
                            self.recorded_frames.append(data)
                        except queue.Empty:
                            continue
            except Exception:
                logger.error("Audio recording error", exc_info=True)
                self.is_recording = False

        self._thread = threading.Thread(target=record)
        self._thread.start()

    def stop_recording(self) -> np.ndarray | None:
        if not self.is_recording:
            return None

        self.is_recording = False
        if self._thread:
            self._thread.join()

        logger.debug("Recording stream closed")

        if not self.recorded_frames:
            return None

        audio_data = np.concatenate(self.recorded_frames, axis=0)
        audio_data = audio_data.flatten().astype(np.float32)

        # RMS normalization: bring audio to consistent level for Whisper
        audio_data = self._normalize_audio(audio_data)
        return audio_data

    @staticmethod
    def _normalize_audio(
        audio: np.ndarray, target_rms: float = _TARGET_RMS
    ) -> np.ndarray:
        """Normalize audio to a target RMS level for consistent transcription."""
        rms = np.sqrt(np.mean(audio**2))
        if rms < 1e-7:
            return audio  # silence, don't amplify noise

        gain = target_rms / rms
        # Clip to prevent extreme amplification/distortion
        gain = max(_MIN_GAIN, min(_MAX_GAIN, gain))
        normalized = audio * gain

        # Soft-clip to [-1, 1] to prevent distortion
        normalized = np.clip(normalized, -1.0, 1.0)
        logger.debug("Audio normalized: rms=%.4f, gain=%.1f", rms, gain)
        return normalized
