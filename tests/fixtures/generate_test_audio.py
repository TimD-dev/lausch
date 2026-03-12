"""Generate synthetic test WAV files for UI testing."""

import math
import os
import struct
import wave


def generate_test_file(
    filename: str = "test_audio.wav",
    duration: int = 10,
    sample_rate: int = 16000,
) -> None:
    """Generate a test WAV file with varying frequencies to simulate speech."""
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    num_samples = duration * sample_rate

    print(f"Generating test audio file: {filename} ({duration}s, {sample_rate}Hz)...")

    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes = 16 bit
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = float(i) / sample_rate
            envelope = (math.sin(2 * math.pi * 2 * t) + 1.0) / 2.0
            envelope *= (math.sin(2 * math.pi * 0.5 * t) + 1.0) / 2.0

            freq = 200 + 100 * math.sin(2 * math.pi * 1.5 * t)
            value = int(32767.0 * 0.8 * envelope * math.sin(2 * math.pi * freq * t))

            data = struct.pack("<h", value)
            wav_file.writeframesraw(data)

    print("Done!")


if __name__ == "__main__":
    generate_test_file()
