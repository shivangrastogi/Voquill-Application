class TranscriptManager:
    """Manages the history of transcribed segments and handles diffing for injection."""
    
    def __init__(self):
        self.history = []
        self.last_injected_text = ""
        self.max_history = 50

    def add_segment(self, text):
        """Adds a new transcribed segment to history."""
        if not text:
            return
        self.history.append(text)
        self.last_injected_text = text
        
        # Maintain history limit
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_last_text(self):
        return self.last_injected_text

    def get_context(self, limit=3):
        """Returns the last 'limit' segments as a single context string."""
        return " ".join(self.history[-limit:])

    def clear(self):
        self.history = []
        self.last_injected_text = ""

    def get_undo_command(self):
        """Generates backspaces to 'undo' the last injected chunk."""
        if not self.last_injected_text:
            return ""
        
        # Number of backspaces needed to remove last segment
        # Plus one for the trailing space added in main.py
        return "\b" * (len(self.last_injected_text) + 1)
