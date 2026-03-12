import pyperclip
import keyboard
import time

class TextInserter:
    def __init__(self):
        self.delay_after_paste = 0.1 # Very small delay to ensure OS handles the paste

    def insert_text(self, text):
        """
        Safely inserts text at the current cursor position by:
        1. Backing up the current clipboard.
        2. Setting clipboard to the transcribed text.
        3. Firing Ctrl+V.
        4. Restoring the original clipboard.
        """
        if not text:
            return

        print(f"Preparing to insert '{text}'...", flush=True)

        # 1. Backup clipboard
        original_clipboard = pyperclip.paste()
        
        try:
            # 2. Set new text
            pyperclip.copy(text)
            
            # 3. Fire Ctrl+V
            keyboard.send('ctrl+v')
            
            # Wait a tiny bit for the OS to process the paste command
            # before we yank the text back out of the clipboard
            time.sleep(self.delay_after_paste)

        except Exception as e:
            print(f"Error during text insertion: {e}")
        finally:
            # 4. Restore original clipboard
            pyperclip.copy(original_clipboard)
            print("Finished insertion and restored clipboard.", flush=True)

# Simple test block
if __name__ == "__main__":
    print("Test will start in 3 seconds. Focus a text field.")
    time.sleep(3)
    inserter = TextInserter()
    inserter.insert_text("Hallo, dies ist ein automatischer Test!")
