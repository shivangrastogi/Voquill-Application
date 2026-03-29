from enum import Enum

class SessionState(Enum):
    IDLE = 0
    LISTENING = 1
    PROCESSING = 2
    INJECTING = 3
    ERROR = 4

class SessionManager:
    """Manages the current state of the dictation session."""
    
    def __init__(self):
        self.state = SessionState.IDLE
        self._current_mode = "Polished"

    def set_state(self, state):
        """Sets the current state."""
        print(f"Session State: {self.state} -> {state}")
        self.state = state

    def get_state(self):
        return self.state

    def set_mode(self, mode):
        """Sets the dictation mode (Polished, Email, Verbatim)."""
        self._current_mode = mode

    def get_mode(self):
        return self._current_mode
