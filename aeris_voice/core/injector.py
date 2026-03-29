import ctypes
import time
from ctypes import wintypes

# Win32 Constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# Low-level structures for SendInput
class KBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("iu", INPUT_UNION)]

class KeyboardInjector:
    """Pro-level Win32 SendInput wrapper for hardware-level typing."""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32

    def type_text(self, text, delay_per_char=0.002):
        """Types text using UNICODE SendInput for maximum compatibility."""
        if not text:
            return

        for char in text:
            # Send Key Down
            inputs = (INPUT * 2)()
            inputs[0].type = INPUT_KEYBOARD
            inputs[0].iu.ki.wVk = 0
            inputs[0].iu.ki.wScan = ord(char)
            inputs[0].iu.ki.dwFlags = KEYEVENTF_UNICODE
            
            # Send Key Up
            inputs[1].type = INPUT_KEYBOARD
            inputs[1].iu.ki.wVk = 0
            inputs[1].iu.ki.wScan = ord(char)
            inputs[1].iu.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            
            self.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))
            
            if delay_per_char > 0:
                time.sleep(delay_per_char)

    def paste_text(self, text):
        """Copies text to clipboard and sends Ctrl+V (Instant)."""
        if not text:
            return
            
        try:
            # 1. Set Clipboard (UTF-16 for Unicode support)
            self._set_clipboard(text)
            
            # 2. Send Ctrl+V
            VK_CONTROL = 0x11
            VK_V = 0x56
            
            # Ctrl Down -> V Down -> V Up -> Ctrl Up
            self.user32.keybd_event(VK_CONTROL, 0, 0, 0)
            self.user32.keybd_event(VK_V, 0, 0, 0)
            self.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            self.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            
            # Small delay to ensure the target app processes the paste
            time.sleep(0.05)
        except Exception as e:
            print(f"[Injector Error] Paste failed: {e}. Falling back to typing.")
            self.type_text(text)

    def _set_clipboard(self, text):
        """Native Win32 Clipboard implementation."""
        if not isinstance(text, str):
            text = str(text)
            
        # CF_UNICODETEXT = 13
        # GMEM_MOVEABLE = 0x0002
        self.user32.OpenClipboard(0)
        self.user32.EmptyClipboard()
        
        encoded_text = text.encode('utf-16-le') + b'\x00\x00'
        h_mem = ctypes.windll.kernel32.GlobalAlloc(0x0002, len(encoded_text))
        p_mem = ctypes.windll.kernel32.GlobalLock(h_mem)
        ctypes.cdll.msvcrt.memcpy(p_mem, encoded_text, len(encoded_text))
        ctypes.windll.kernel32.GlobalUnlock(h_mem)
        
        self.user32.SetClipboardData(13, h_mem)
        self.user32.CloseClipboard()

    def press_key(self, vk_code):
        """Simulates a single virtual key press."""
        self.user32.keybd_event(vk_code, 0, 0, 0) # Key Down
        self.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0) # Key Up
