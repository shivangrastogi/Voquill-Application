import pygetwindow as gw

class WindowTracker:
    """Tracks and locks the active window for safe text injection."""
    
    def __init__(self):
        self.target_hwnd = None
        self.target_title = None

    def _get_clean_title(self):
        """Returns the current window title cleaned of hidden characters."""
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                # Remove zero-width spaces and other common invisible characters
                clean_title = active_window.title.replace('\u200b', '').strip()
                return clean_title
            return ""
        except Exception:
            return ""

    def lock_current_window(self):
        self.target_title = self._get_clean_title()
        if self.target_title:
            print(f"[Window Locked]: {self.target_title}")

    def is_target_active(self):
        if not self.target_title:
            return True # No lock, allow
        
        current_title = self._get_clean_title()
        return current_title == self.target_title
