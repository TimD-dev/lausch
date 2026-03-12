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


class AudioRecorder:
    def __init__(self, config: AudioConfig = AudioConfig()) -> None:
        self.config = config
        self.is_recording = False
        self.audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._thread: threading.Thread | None = None
        self.recorded_frames: list[np.ndarray] = []
        self.on_audio_data: Callable[[list[float]], None] | None = None

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
                vol = min(1.0, rms * self.config.volume_boost_factor)
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
        return audio_data
