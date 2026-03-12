import wave
import struct
import math
import os

def generate_test_file(filename="test_audio.wav", duration=10, sample_rate=16000):
    """Generates a test WAV file with varying frequencies to simulate speech."""
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    num_samples = duration * sample_rate
    
    print(f"Generating test audio file: {filename} ({duration}s, {sample_rate}Hz)...")
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2) # 2 bytes = 16 bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Create a wave that varies in amplitude and frequency
            # Base frequency 200 Hz, modulated by lower frequencies to act like syllables
            envelope = (math.sin(2 * math.pi * 2 * t) + 1.0) / 2.0  # 0 to 1
            envelope *= (math.sin(2 * math.pi * 0.5 * t) + 1.0) / 2.0 # slower modulation
            
            freq = 200 + 100 * math.sin(2 * math.pi * 1.5 * t)
            value = int(32767.0 * 0.8 * envelope * math.sin(2 * math.pi * freq * t))
            
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
            
    print("Done!")

if __name__ == "__main__":
    generate_test_file()
