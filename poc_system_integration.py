import keyboard
import pyperclip
import time
import threading

def inject_and_restore(text_to_inject):
    print("Iniziere Text-Injektion...")
    # 1. Backup der aktuellen Zwischenablage
    original_clipboard = pyperclip.paste()
    print(f"[Backup] Gesichert: {original_clipboard!r}")
    
    try:
        # 2. Neuen Text in die Zwischenablage legen
        pyperclip.copy(text_to_inject)
        print(f"[Set] Zwischenablage aktualisiert: {text_to_inject!r}")
        
        # Dem System kurz Zeit geben, die Zwischenablage-Änderung zu registrieren
        time.sleep(0.05)
        
        # 3. Tastendruck (Strg+V) simulieren, um einzufügen
        print("[Event] Sende Strg+V...")
        keyboard.send('ctrl+v')
        
        # 4. WICHTIG: Einen Moment warten, damit das Betriebssystem das Einfügen 
        # abschließt, BEVOR wir die Ziel-Zwischenablage "wegziehen".
        time.sleep(0.15)
        
    finally:
        # 5. Restore des Backups
        pyperclip.copy(original_clipboard)
        print(f"[Restore] Zwischenablage wiederhergestellt: {original_clipboard!r}")
        print("Injektion abgeschlossen.\n")

def on_hotkey_pressed():
    print("\n[Event] Hotkey gedrückt! Simuliere Transkription... (wartet 2s)")
    # Da wir uns in einem Callback befinden, starten wir die Injektion besser in einem Thread,
    # um den Keyboard-Hook nicht zu blockieren.
    def worker():
        # Simuliere Whisper-Audio-Verarbeitung
        time.sleep(2)
        dummy_text = "Hallo von Lausch! Dies ist ein transkribierter Text (eingefügt durch den PoC)."
        inject_and_restore(dummy_text)
        
    threading.Thread(target=worker).start()

def main():
    print("=== System Integration PoC gestartet ===")
    hotkey = 'ctrl+space'
    print(f"Lausche auf Hotkey: {hotkey}")
    print("1. Gehe in ein beliebiges Textfeld (z.B. Notepad, Browser)")
    print(f"2. Drücke {hotkey}")
    print("3. Warte ca. 2 Sekunden auf das Einfügen des Textes.")
    print("--> Drücke 'esc' in der Konsole / irgendwo, um das Skript zu beenden.\n")
    
    # Hotkey registrieren
    keyboard.add_hotkey(hotkey, on_hotkey_pressed)
    
    # Skript blockieren und am Leben halten, bis 'esc' gedrückt wird
    keyboard.wait('esc')
    print("PoC beendet.")

if __name__ == "__main__":
    main()
