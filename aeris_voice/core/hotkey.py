import keyboard
import threading

class HotkeyListener:
    """Listens for a global hotkey combination to toggle dictation."""
    
    def __init__(self, toggle_key="ctrl+windows", callback=None):
        # keyboard library uses names like 'ctrl+windows' skip '<' and '>'
        self.toggle_key = toggle_key.replace("<", "").replace(">", "").replace("cmd", "windows")
        self.callback = callback
        self.active = False

    def _on_activate(self):
        self.active = not self.active
        print(f"\n[Hotkey] Dictation {'Active' if self.active else 'Inactive'}")
        if self.callback:
            self.callback(self.active)

    def start(self):
        """Starts the listener using the 'keyboard' library for better Windows stability."""
        try:
            keyboard.add_hotkey(self.toggle_key, self._on_activate, suppress=False)
            print(f"Hotkey Listener Started (Combo: {self.toggle_key})")
        except Exception as e:
            print(f"Failed to start Hotkey Listener: {e}")

    def stop(self):
        keyboard.remove_all_hotkeys()
