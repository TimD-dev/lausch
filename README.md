# Lausch

**Lausch** (German for *"listen"*) is a privacy-first, offline dictation app for Windows. It captures your voice, transcribes it locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and inserts the text wherever your cursor is — no cloud, no account, no data leaves your machine.

## Features

- **Fully offline** — runs entirely on your CPU, no internet required after model download
- **Global hotkey** — press `Ctrl+Space` to start/stop dictation from any app
- **Auto-paste** — transcribed text is inserted at your cursor position instantly
- **Multilingual** — optimized for German and English with language-specific prompts
- **Audio normalization** — adaptive gain ensures consistent recognition regardless of mic volume
- **Smooth visualizer** — animated overlay shows mic activity with interpolated bars
- **System tray** — lives in your taskbar with quick access to settings
- **Configurable** — language, model size, microphone, shortcut, UI position, and autostart
- **Persistent settings** — saved to `%APPDATA%\Lausch\settings.json`

## How It Works

1. **Start** — launch Lausch, it loads the Whisper model and waits in the system tray
2. **Record** — press `Ctrl+Space`, the overlay appears with an audio visualizer
3. **Speak** — talk naturally, the bars animate in response to your voice
4. **Stop** — press `Ctrl+Space` again, audio is normalized and transcribed
5. **Insert** — text is pasted at your cursor via clipboard (original clipboard is restored)
6. **Quit** — press `Esc` or right-click the tray icon → Quit

## Project Structure

```
lausch/
├── pyproject.toml                    # Project metadata & dependencies
├── lausch.spec                       # PyInstaller build config
├── README.md
├── scripts/
│   └── build.py                      # Build automation
├── installer/
│   └── lausch_setup.iss              # Inno Setup installer script
├── assets/
│   └── icon.ico                      # App icon
├── lausch/                           # Main package
│   ├── __init__.py
│   ├── __main__.py                   # Entry point (python -m lausch)
│   ├── main.py                       # App orchestrator & hotkey polling
│   ├── config.py                     # Dataclass configs (Audio, UI, Keyboard, etc.)
│   ├── settings.py                   # JSON-based persistent settings
│   ├── logging_setup.py              # Logging configuration
│   ├── autostart.py                  # Windows autostart registry helper
│   ├── audio/
│   │   └── recorder.py              # Mic capture, adaptive gain, RMS normalization
│   ├── transcription/
│   │   └── transcriber.py           # faster-whisper integration with VAD
│   ├── input/
│   │   └── text_inserter.py         # Clipboard-based text injection
│   └── ui/
│       ├── overlay.py               # Frameless desktop overlay window
│       ├── visualizer.py            # Smooth animated audio bar widget
│       ├── settings_window.py       # Settings UI (Times New Roman design)
│       └── tray.py                  # System tray icon & menu
└── tests/
    ├── conftest.py
    └── test_overlay.py
```

## Installation

### From source (development)

```bash
git clone https://github.com/TimD-dev/lausch.git
cd lausch

python -m venv .venv
.venv\Scripts\activate

pip install -e ".[dev]"
```

### From installer

Download `LauschSetup.exe` from [Releases](https://github.com/TimD-dev/lausch/releases) and run it. No Python required.

## Usage

```bash
python -m lausch
```

On first launch, the Whisper model (~460 MB for `small`) is downloaded automatically. Subsequent starts are fast.

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Space` | Start / stop recording |
| `Esc` | Quit the application |

### Settings

Right-click the system tray icon → **Settings** to configure:

| Setting | Options | Default |
|---|---|---|
| Language | Auto, Deutsch, English | Auto |
| Model | tiny, base, small, medium | small |
| Microphone | System default or specific device | Default |
| Shortcut | Any key combination | Ctrl+Space |
| UI Position | Bottom, Top | Bottom |
| Autostart | On/Off | Off |

## Tech Stack

| Component | Library |
|---|---|
| Speech recognition | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) |
| Audio capture | [sounddevice](https://python-sounddevice.readthedocs.io/) + NumPy |
| Desktop UI | [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) |
| Global hotkeys | [keyboard](https://github.com/boppreh/keyboard) |
| Clipboard | [pyperclip](https://github.com/asweigart/pyperclip) |
| Packaging | [PyInstaller](https://pyinstaller.org/) + [Inno Setup](https://jrsoftware.org/isinfo.php) |

## Build

```bash
# Build standalone executable
pyinstaller lausch.spec

# Create Windows installer (requires Inno Setup)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\lausch_setup.iss
```

## Privacy

All audio processing happens locally. No data is sent to any server. The Whisper model runs on your CPU — your voice never leaves your machine.

## License

MIT
