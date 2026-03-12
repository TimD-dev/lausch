# Lausch App

**Lausch** (German for "listen") is a locally running dictation application that utilizes the faster-whisper model to provide quick and privacy-focused speech-to-text functionality. Instead of sending audio to the cloud, it transcribes your speech locally on your machine and quickly types it out for you wherever your keyboard cursor currently is.

## Functionality

1. **Global Hotkey:** The application runs in the background. Press `Ctrl + Space` to start recording.
2. **Dictation:** Speak into your microphone.
3. **Stop & Process:** Press `Ctrl + Space` again to stop the recording.
4. **Transcription:** The faster-whisper model will process the recorded audio locally to detect your speech.
5. **Auto-Type Insertion:** The app seamlessly inserts the transcribed text by temporarily copying it to your clipboard, triggering a `Ctrl + V` paste command at your current cursor position, and then immediately restoring the contents of your original clipboard.

You can stop the application entirely by pressing the `Esc` key.

## Project Structure

The project is structured efficiently to separate logic into distinct modules within the `src` directory, managed by the entry point `main.py`.

```text
lausch/
│
├── main.py                     # Entry point for the application. It runs the PyQt6 main loop
│                               # and creates a robust polling background thread to monitor 
│                               # keyboard shortcuts ('Ctrl + Space') to safely orchestrate 
│                               # the recording, transcription, and UI without blocking.
│
├── learnings.md                # A deep-dive document explaining how all the components work
│                               # dynamically under the hood. Great for learning Python patterns!
│
└── src/                        # Core application modules
    ├── audio_recorder.py       # Handles reading data from your microphone using sounddevice
    │                           # and storing it into a numpy array for direct processing.
    │
    ├── transcriber.py          # Interfaces with the local faster-whisper model to turn
    │                           # the audio data into text.
    │
    ├── text_inserter.py        # Handles the complex task of simulating text entry by securely 
    │                           # preserving clipboard history, pasting the new text, and restoring.
    │
    └── ui/                     # Frontend modules
        └── overlay.py          # A borderless PyQt6 desktop overlay with a dynamic audio visualizer.
```

## Requirements

The app utilizes several third-party libraries:
- `PyQt6` for the modern, hardware-accelerated desktop overlay UI.
- `keyboard` for safe background global shortcut polling (`is_pressed`).
- `sounddevice` for microphone input and `numpy` for data handling.
- `faster-whisper` for the actual transcription engine.
- `pyperclip` for clipboard management during the text insertion phase.

By leveraging a local machine learning model, it guarantees dictation tasks are kept local and private.

## 📦 Build Instructions

To build a standalone Windows executable, use the provided `build.py` script. This uses PyInstaller to bundle the application along with all heavy machine learning dependencies.

### Prerequisites
Make sure PyInstaller is installed:
```bash
pip install pyinstaller
```

### Running the Build
1. Open a terminal in the project directory.
2. Run the build script:
   ```bash
   python build.py
   ```
3. The script will clean up old builds and generate the application in `--onedir` mode.
4. Once completed, the application will be located inside the `dist/lausch` directory. 
5. You can run the application by launching `dist/lausch/lausch.exe`.
6. To distribute the app, simply zip the entire `dist/lausch` folder.

*Note: On the first launch of `lausch.exe`, it will dynamically download the required `faster-whisper` model into the HuggingFace cache directory if it's not already present. Subsequent launches will be significantly faster.*
