import ollama
import json

class AICleaner:
    """Uses a local LLM (Ollama) to clean up and polish transcripts."""
    
    def __init__(self, model="mistral"):
        self.model = model
        self.modes = {
            "Polished": "Clean the following speech text. Remove filler words (um, uh), fix grammar, and keep Hindi words unchanged. Do NOT translate Hindi to English. Return only the corrected text.",
            "Email": "Transform the following speech into a professional email style. Keep any Hindi context intact but ensure the tone is formal. Return only the email body.",
            "Verbatim": "Keep the text exactly as it is, but fix basic punctuation. Do not remove filler words."
        }
        try:
            # Check if ollama server is reachable
            ollama.list()
            self.available = True
            print(f"AICleaner initialized with model: {self.model}")
        except Exception as e:
            self.available = False
            print(f"AI Cleanup Warning: Could not connect to Ollama. Cleanup will be disabled. Error: {e}")

    def clean(self, text, mode="Polished"):
        """Cleans the text based on the selected mode."""
        if not text:
            return ""

        if not self.available:
            # Fallback: Basic rule-based cleanup if AI is unavailable
            return self._basic_cleanup(text)

        instruction = self.modes.get(mode, self.modes["Polished"])
        prompt = f"{instruction}\n\nSpeech Input:\n{text}\n\nOutput:\n"
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'num_predict': 128, 'temperature': 0.3} # Optimize for speed
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"AI Cleanup Error: {e}")
            return self._basic_cleanup(text)

    def _basic_cleanup(self, text):
        """Simple rule-based cleanup as fallback."""
        import re
        # Remove common fillers
        fillers = [r'\bum\b', r'\buh\b', r'\bah\b', r'\blike\b', r'\byou know\b']
        cleaned = text
        for f in fillers:
            cleaned = re.sub(f, '', cleaned, flags=re.IGNORECASE)
        # Fix double spaces and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'
        return cleaned.capitalize()
