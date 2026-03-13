"""Speech-to-text transcription using the faster-whisper model."""

from __future__ import annotations

import logging

import numpy as np
from faster_whisper import WhisperModel

from lausch.config import TranscriberConfig

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self, config: TranscriberConfig = TranscriberConfig()) -> None:
        """
        Initialize the faster-whisper model.

        model_size: "tiny", "base", "small", "medium", "large-v3"
        device: "cpu" or "cuda"
        compute_type: "int8" or "float16" (if using cuda)

        Using 'tiny' or 'base' with int8 is highly recommended for speed on CPU.
        """
        self.config = config
        logger.info("Loading Whisper model '%s'...", config.model_size)
        self.model = WhisperModel(
            config.model_size,
            device=config.device,
            compute_type=config.compute_type,
        )
        logger.info("Model loaded, running warmup...")
        self._warmup()

    def _warmup(self) -> None:
        """Run a dummy inference to load the model fully into memory and cache."""
        try:
            dummy_audio = np.zeros(
                self.config.warmup_duration_samples, dtype=np.float32
            )
            list(self.model.transcribe(dummy_audio, beam_size=1))
            logger.info("Warmup complete")
        except Exception as e:
            logger.warning("Warmup failed (ignoring): %s", e)

    def transcribe(self, audio_data: np.ndarray | None) -> str:
        """Transcribe the given audio data (numpy 1D array) and return the text."""
        if audio_data is None or len(audio_data) == 0:
            logger.warning("No audio data provided")
            return ""

        logger.debug("Transcribing audio...")

        segments, info = self.model.transcribe(
            audio_data,
            beam_size=self.config.beam_size,
            vad_filter=self.config.vad_filter,
            vad_parameters=dict(
                min_silence_duration_ms=self.config.vad_min_silence_ms
            ),
            language=self.config.language,
            initial_prompt=self.config.initial_prompt,
        )

        logger.info(
            "Detected language '%s' (p=%.2f)",
            info.language,
            info.language_probability,
        )

        full_text = " ".join(segment.text for segment in segments)
        return full_text.strip()
