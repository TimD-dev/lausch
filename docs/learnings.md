# Learnings: How Lausch Works Under the Hood

This document breaks down the interesting parts of the `lausch` codebase so you can learn from how it was built. It covers the Python concepts and the libraries used to make the application function seamlessly.

## 1. Global Hotkeys (`keyboard` library)

**File: `main.py`**

The `keyboard` library is used to listen for keystrokes globally. However, to maintain system stability and avoid locking keyboard hooks, the application uses a safe polling thread.

```python
# main.py - Line 47
is_pressed = keyboard.is_pressed(shortcut)
if is_pressed and not was_pressed:
    self.toggle_recording()
    
# main.py - Line 66
self.poll_thread = threading.Thread(target=self._poll_shortcut, args=(shortcut,), daemon=True)
```

*   **`keyboard.is_pressed(...)`**: This function securely checks the boolean state if a key (like `ctrl+space`) is currently held down without stealing the event from other apps.
*   **Polling Loop (`time.sleep(0.05)`)**: The dedicated `self._poll_shortcut` thread runs continuously in the background checking `is_pressed`. We use a small `time.sleep` pause so it doesn't max out the CPU. 
*   **Main Thread (`keyboard.is_pressed('esc')`)**: The main script also polls for the `Escape` key similarly to keep the application alive indefinitely until requested to exit securely.

## 2. Audio Recording Threads (`threading`, `sounddevice`, `numpy`)

**File: `src/audio_recorder.py`**

Recording audio while letting the rest of the application run requires understanding *concurrency* (doing multiple things at once).

```python
# src/audio_recorder.py
self._record_thread = threading.Thread(target=self._recording_loop)
self._record_thread.start()
```

*   **Why use Threads?** If we ran the recording loop in the main program flow, the entire application would freeze or "block" while it recorded. You wouldn't be able to press the hotkey again to stop it! By putting the `record` function into a separate `threading.Thread`, it runs in the background.
*   **`sounddevice`**: Used to actually capture the audio stream from your microphone. It continuously feeds small chunks of audio data into a `queue.Queue`.
*   **`numpy`**: Instead of slowly writing data to a `.wav` file on the hard drive, we store the audio chunks dynamically in the computer's RAM using mathematically optimized `numpy` arrays. This makes the transition to the AI model significantly faster.

## 3. The Power of Queues (`queue` module)

**File: `src/audio_recorder.py`**

When dealing with threads, getting them to talk to each other safely can be tricky. A `queue.Queue` is a thread-safe way to pass data.

```python
# src/audio_recorder.py 
self.audio_queue.put(indata.copy())

# src/audio_recorder.py
chunk = self.audio_queue.get()
```

*   One thread (the `sounddevice` callback) is constantly shouting "Here's more audio data!" and throwing it into the queue using `.put()`.
*   The other thread (our custom `_recording_loop` function) is listening and continuously picking that data out.

## 4. Thread-Safe UI Updates (`PyQt6 Signals`)

**File: `main.py` & `src/ui/overlay.py`**

Building Desktop UIs with `PyQt6` introduces a strict rule: You can only update the UI from the *Main Thread*. Since our audio is recorded in a *Background Thread*, we need a safe way to send data (like volume levels for an animation) to the screen.

```python
# main.py
class AppSignals(QObject):
    update_audio = pyqtSignal(list)
    
# ... connecting the signal to the UI ...
self.signals.update_audio.connect(self.ui.visualizer.update_amplitudes)

# ... emitting from the background recording ...
self.recorder.on_audio_data = self.signals.update_audio.emit
```

*   **`pyqtSignal`**: Think of this as a custom event channel. 
*   **`.connect(...)`**: We wire the channel to a specific function in our UI (the visualizer update).
*   **`.emit(...)`**: When the background thread gets new audio data, it "emits" it into the channel. PyQt safely catches this data and schedules the UI update correctly in the Main Thread, preventing crashes!

## 5. Local AI Inference (`faster-whisper`)

**File: `src/transcriber.py`**

The core "magic" is turning audio into text without sending it to the cloud.

```python
# src/transcriber.py
self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

# src/transcriber.py
segments, info = self.model.transcribe(audio_data, beam_size=5)
```

*   **`faster-whisper`**: This is an optimized version of OpenAI's Whisper model. By initializing it with parameters like `"tiny"` and `"cpu"`, it ensures the model is small enough to run quickly on standard computer processors without needing an expensive graphics card (GPU).
*   **`model.transcribe()`**: Takes the path to our temporarily saved `.wav` file. It returns `segments` (the actual transcribed words broken into chunks) and `info` (metadata like the detected language and how confident the model is).

## 5. Simulating User Input Safely (`pyperclip`, `keyboard`)

**File: `src/text_inserter.py`**

The final step is putting the text wherever your cursor is.

```python
# src/text_inserter.py - Lines 23-40
original_clipboard = pyperclip.paste()
try:
    pyperclip.copy(text)
    keyboard.send('ctrl+v')
    time.sleep(self.delay_after_paste)
finally:
    pyperclip.copy(original_clipboard)
```

1.  **Backup**: It first grabs whatever you currently have copied (`pyperclip.paste()`) so it doesn't destroy your clipboard history.
2.  **Copy & Paste**: It copies the transcribed text and simulates pressing `Ctrl+V` (`keyboard.send('ctrl+v')`) to paste it. This is much faster and more reliable than simulating keypresses character by character.
3.  **Restore**: The `finally:` block is critical. It guarantees that even if the paste operation fails for some reason, your original clipboard contents are put back. The `time.sleep()` is necessary because the OS takes a tiny fraction of a second to realize `Ctrl+V` was pressed and grab the text. If we restored the clipboard *instantly*, it might paste your old data instead!

## 7. Compiling to a Standalone Executable (`PyInstaller`)

**File: `build.py` & `lausch.spec`**

Writing a Python script is great, but sharing it with someone who doesn't have Python installed requires bundling it into a `.exe`.

```bash
# Executed via build.py
pyinstaller --noconfirm lausch.spec
```

*   **`PyInstaller`**: This tool scans your `main.py` entry point, finds every single dependency (like PyQt6, faster-whisper, numpy), and packages them alongside an embedded Python interpreter into a single `dist/` folder.
*   **`.spec` file**: This is a configuration file. It tells PyInstaller exactly *how* to build the app. For example, it defines that the app shouldn't open an ugly black console window (`console=False`), which extra data files to include, or what icon to use. 

## Conclusion

By combining hotkeys, multi-threading, local AI models, hardware-accelerated UIs, and clipboard manipulation, Lausch creates a smooth workflow entirely on your local machine. These patterns—managing threads with queues, thread-safe UI signaling, and compiling native executables—are fundamental skills for building robust Python applications.
