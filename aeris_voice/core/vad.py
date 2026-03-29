import torch
import numpy as np

class VADProcessor:
    """High-performance Silero VAD wrapper for speech detection."""
    
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        # Load Silero VAD model (local or via torch hub)
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            trust_repo=True
        )
        (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks) = utils
        print("Silero VAD Loaded.")

    def is_speech(self, audio_chunk, sample_rate=16000):
        """Returns True if any sub-chunk contains speech based on Silero confidence."""
        # Ensure audio is float32 tensor
        if not isinstance(audio_chunk, torch.Tensor):
            audio_chunk = torch.from_numpy(audio_chunk.flatten().astype("float32"))
        
        # Silero VAD expects 512 samples for 16000Hz
        # If chunk is larger (e.g. 8000 samples), we need to check sub-chunks
        window_size = 512
        num_samples = audio_chunk.shape[-1]
        
        if num_samples > window_size:
            # Check a few windows within the chunk for speech
            for i in range(0, num_samples - window_size, window_size):
                sub_chunk = audio_chunk[i : i + window_size]
                with torch.no_grad():
                    speech_prob = self.model(sub_chunk, sample_rate).item()
                if speech_prob > self.threshold:
                    return True
            return False
        else:
            # Pad if too small
            if num_samples < window_size:
                audio_chunk = torch.nn.functional.pad(audio_chunk, (0, window_size - num_samples))
            
            with torch.no_grad():
                speech_prob = self.model(audio_chunk, sample_rate).item()
            return speech_prob > self.threshold
