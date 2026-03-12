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

```text
lausch/
├── pyproject.toml                   # Project metadata & dependencies
├── lausch.spec                      # PyInstaller configuration
├── README.md
├── docs/
│   ├── learnings.md                 # Technical deep-dive documentation
│   └── agent_roles.md               # Multi-agent development guide
├── scripts/
│   └── build.py                     # PyInstaller build automation
├── lausch/                          # Python package
│   ├── __init__.py
│   ├── __main__.py                  # Entry point for `python -m lausch`
│   ├── main.py                      # Application orchestrator
│   ├── config.py                    # Central configuration (all constants)
│   ├── logging_setup.py             # Logging configuration
│   ├── audio/
│   │   └── recorder.py             # Microphone capture with threading
│   ├── transcription/
│   │   └── transcriber.py          # Whisper model integration
│   ├── input/
│   │   └── text_inserter.py        # Clipboard-based text injection
│   └── ui/
│       ├── overlay.py              # Desktop overlay window
│       └── visualizer.py           # Audio bar visualizer widget
└── tests/
    ├── conftest.py                  # Shared pytest fixtures
    └── test_overlay.py              # UI overlay test
```

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd lausch

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Run the application
python -m lausch
```

## Requirements

The app utilizes several third-party libraries:
- `PyQt6` for the modern, hardware-accelerated desktop overlay UI.
- `keyboard` for safe background global shortcut polling (`is_pressed`).
- `sounddevice` for microphone input and `numpy` for data handling.
- `faster-whisper` for the actual transcription engine.
- `pyperclip` for clipboard management during the text insertion phase.

By leveraging a local machine learning model, it guarantees dictation tasks are kept local and private.

## Build Instructions

To build a standalone Windows executable, use the provided build script.

### Prerequisites
```bash
pip install -e ".[dev]"
```

### Running the Build
```bash
python scripts/build.py
```

The application will be generated in `--onedir` mode inside the `dist/lausch` directory. To distribute, zip the entire `dist/lausch` folder.

*Note: On the first launch, the required `faster-whisper` model will be downloaded automatically. Subsequent launches will be significantly faster.*
