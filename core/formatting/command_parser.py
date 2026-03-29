class CommandParser:
    """Parses spoken commands into punctuation or actions."""
    
    def __init__(self):
        # Mapping spoken words to symbols/actions
        self.basic_commands = {
            "comma": ",",
            "period": ".",
            "full stop": ".",
            "question mark": "?",
            "new line": "\n",
            "next line": "\n",
            "paragraph": "\n\n",
            "hyphen": "-",
            "exclamation mark": "!"
        }

    def parse(self, text):
        """Replaces spoken commands with their respective symbols."""
        if not text:
            return ""
            
        processed_text = text.lower()
        
        # Simple string replacement for now
        # In a more advanced version, this would use NLP or regex
        for command, replacement in self.basic_commands.items():
            processed_text = processed_text.replace(f" {command} ", replacement)
            processed_text = processed_text.replace(f"{command} ", replacement)
            processed_text = processed_text.replace(f" {command}", replacement)
            
        # Capitalize first letter of sentences
        # (This is basic; a more robust version could use the AI cleaner)
        return processed_text.strip()
