from faster_whisper import WhisperModel
import numpy as np

class STT:
    """Configurable Faster-Whisper wrapper with Warmup."""
    
    def __init__(self, model_size="base", compute_type="int8"):
        print(f"[Engine] Loading Whisper '{model_size}' ({compute_type})...")
        try:
            self.model = WhisperModel(model_size, compute_type=compute_type)
            # Warmup
            self.transcribe(np.zeros(16000, dtype="float32"))
            print("[Engine] STT Ready.")
        except Exception as e:
            print(f"[Engine Error] Could not load STT: {e}")
            raise

    def transcribe(self, audio):
        """Transcribes audio array and returns combined text."""
        try:
            segments, _ = self.model.transcribe(audio, beam_size=1)
            text = "".join([seg.text for seg in segments])
            return text.strip()
        except Exception as e:
            print(f"[transcribe error]: {e}")
            return ""
