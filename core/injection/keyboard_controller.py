import pyperclip
import keyboard
import time
from pynput.keyboard import Controller

class KeyboardController:
    """Injects text into the system using clipboard or simulated typing."""
    
    def __init__(self):
        self.pynput_controller = Controller()

    def inject(self, text, method="clipboard"):
        """
        Injects text into the active window.
        Methods: 'clipboard' (fastest), 'typing' (fallback).
        """
        if not text:
            return

        if method == "clipboard":
            self._inject_clipboard(text)
        else:
            self._inject_typing(text)

    def _inject_clipboard(self, text):
        """Copies text to clipboard and simulates CTRL+V."""
        # Save original clipboard content (optional, but complex in some OS)
        pyperclip.copy(text)
        
        # Short delay to ensure clipboard is ready
        time.sleep(0.1)
        
        # Simulate paste
        keyboard.press_and_release('ctrl+v')

    def _inject_typing(self, text):
        """Simulates character-by-character typing."""
        for char in text:
            self.pynput_controller.type(char)
            time.sleep(0.01) # Small delay for reliability
