from faster_whisper import WhisperModel
import os
import torch
import re

class Transcriber:
    """Converts audio buffer to text using faster-whisper for high performance."""
    
    def __init__(self, model_size="base"):
        """
        Model sizes: tiny, base, small, medium, large.
        """
        print(f"Loading Faster-Whisper model '{model_size}'...")
        
        # Determine device and compute type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "int8" if self.device == "cpu" else "float16"
        
        # Custom model path
        model_path = os.path.join("models", "whisper")
        os.makedirs(model_path, exist_ok=True)
        
        self.model = WhisperModel(
            model_size, 
            device=self.device, 
            compute_type=self.compute_type,
            download_root=model_path
        )
        print(f"Faster-Whisper model loaded on {self.device} with {self.compute_type}.")

    def transcribe(self, audio_data, initial_prompt="Hinglish speech mixing Hindi and English."):
        """
        Transcribed segments with strict confidence thresholds to block hallucinations.
        """
        # Optimized transcribe call for Hinglish, low latency, and hallucination rejection
        segments, info = self.model.transcribe(
            audio_data,
            language="en",
            beam_size=1,
            best_of=1,
            temperature=0,
            vad_filter=True,
            initial_prompt=initial_prompt,
            no_speech_threshold=0.6,    # Reject silence accurately
            logprob_threshold=-1.0       # Reject low-confidence guesses
        )
        
        # Combined text from segments that are not hallucinations
        blacklist = ["music", "thank you", "the end", "thanks for watching", "subtitles by", "bye"]
        
        text_parts = []
        for segment in segments:
            clean_segment = segment.text.strip().lower().strip(".,?!")
            if clean_segment in blacklist:
                print(f"Hallucination Blocked: '{segment.text}'")
                continue
            text_parts.append(segment.text)

        text = " ".join(text_parts).strip()
        
        # Filter garbage non-ASCII characters if any
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        return text
