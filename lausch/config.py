"""Central configuration for all Lausch application constants."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    queue_timeout: float = 0.1
    visualizer_bar_count: int = 10
    volume_boost_factor: float = 15.0


@dataclass(frozen=True)
class TranscriberConfig:
    model_size: str = "tiny"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 2
    vad_filter: bool = True
    vad_min_silence_ms: int = 500
    warmup_duration_samples: int = 16000  # 1 second at 16kHz


@dataclass(frozen=True)
class UIConfig:
    window_width: int = 200
    window_height: int = 60
    taskbar_offset: int = 60
    corner_radius: int = 15
    layout_margins: tuple[int, int, int, int] = (20, 10, 20, 10)
    layout_spacing: int = 15
    logo_font_family: str = "Times New Roman"
    logo_font_size: int = 28
    color_background: str = "#F4EFE6"
    color_accent: str = "#E07A5F"
    color_border: str = "#E5E0D8"
    bar_spacing: int = 4
    min_amplitude: float = 0.05
    visualizer_min_width: int = 100
    visualizer_min_height: int = 30


@dataclass(frozen=True)
class KeyboardConfig:
    toggle_shortcut: str = "ctrl+space"
    exit_shortcut: str = "esc"
    poll_interval: float = 0.05
    error_retry_delay: float = 1.0


@dataclass(frozen=True)
class InsertionConfig:
    delay_after_paste: float = 0.1
    delay_before_paste: float = 0.2


@dataclass(frozen=True)
class AppConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    transcriber: TranscriberConfig = field(default_factory=TranscriberConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    keyboard: KeyboardConfig = field(default_factory=KeyboardConfig)
    insertion: InsertionConfig = field(default_factory=InsertionConfig)
