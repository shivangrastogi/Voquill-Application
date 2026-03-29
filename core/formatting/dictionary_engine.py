import re

class DictionaryEngine:
    """Handles global text replacements (auto-correct, acronyms, brand names)."""
    
    def __init__(self, dictionary_map=None):
        """
        dictionary_map: Dict of {pattern: replacement}
        """
        self.dictionary = dictionary_map or {}

    def update_dictionary(self, dictionary_map):
        self.dictionary = dictionary_map

    def apply(self, text):
        """Applies all dictionary replacements using case-insensitive regex."""
        if not text:
            return ""
            
        for word, replacement in self.dictionary.items():
            if not replacement:
                continue
            # \b matches word boundaries
            pattern = r"\b" + re.escape(word) + r"\b"
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        return text

    @staticmethod
    def load_from_db(db_manager):
        """Factory method to create an engine from the database."""
        # Note: We need a method in db_manager to get the word->replacement map
        # For now, we'll assume the db_manager returns a list of tuples or dict
        pass
