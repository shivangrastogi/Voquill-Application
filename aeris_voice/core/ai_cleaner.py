import time
import os

class AICleaner:
    """Multi-provider AI Cleaner supporting local (Ollama) and cloud (Hugging Face, Groq)."""
    
    def __init__(self, provider="ollama", model="mistral", api_key=None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.system_prompt = "Act as a professional editor. Clean the following speech text: remove stutters, fix punctuation, and keep the meaning exact. Output ONLY the cleaned text."
        
        # Lazy imports to avoid heavy dependencies if not used
        self.client = None
        self._setup_client()

    def _setup_client(self):
        try:
            if self.provider == "huggingface":
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(api_key=self.api_key)
            elif self.provider == "groq":
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=self.api_key
                )
            elif self.provider == "ollama":
                import ollama
                self.client = ollama
        except ImportError as e:
            print(f"[AI Error] Missing library for {self.provider}: {e}")

    def polish(self, text, context="", timeout=3.0):
        if not text or not self.client:
            return text

        full_prompt = f"System: {self.system_prompt}\nContext: {context}\nInput: {text}\nOutput:"

        try:
            start_time = time.time()
            
            if self.provider == "huggingface":
                response = self.client.text_generation(
                    full_prompt, 
                    model=self.model, 
                    max_new_tokens=128,
                    stop_sequences=["\n", "System:"]
                )
                result = response.strip()
            
            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Context: {context}\nInput: {text}"}
                    ],
                    max_tokens=128,
                    temperature=0.1
                )
                result = response.choices[0].message.content.strip()
            
            else: # Fallback to Ollama
                response = self.client.generate(
                    model=self.model,
                    prompt=full_prompt,
                    options={"num_predict": 128, "temperature": 0.1, "stop": ["\n", "System:"]}
                )
                result = response['response'].strip()

            if (time.time() - start_time) > timeout:
                return text
                
            return result
        except Exception as e:
            print(f"[AI Error] {self.provider} failed: {e}")
            return text
