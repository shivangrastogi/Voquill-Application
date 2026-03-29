import keyboard
import threading

class HotkeyListener:
    """Listens for global hotkeys to trigger dictation."""
    
    def __init__(self, hotkey="ctrl+alt+v", callback=None):
        self.hotkey = hotkey
        self.callback = callback
        self._running = False

    def _on_hotkey(self):
        """Internal callback when hotkey is pressed."""
        if self.callback:
            self.callback()

    def start(self):
        """Starts the global hotkey listener in the background."""
        if self._running:
            return
        
        self._running = True
        keyboard.add_hotkey(self.hotkey, self._on_hotkey)
        print(f"Hotkey Listener started: {self.hotkey}")

    def stop(self):
        """Stops the listener."""
        self._running = False
        keyboard.remove_hotkey(self.hotkey)
        print("Hotkey Listener stopped.")

    def wait(self):
        """Blocks the calling thread until a key is pressed (for testing)."""
        keyboard.wait()
