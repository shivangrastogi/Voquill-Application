import numpy as np

class AudioBuffer:
    """Manages a sliding window of audio data."""
    
    def __init__(self, sample_rate=16000, max_duration_sec=30):
        self.sample_rate = sample_rate
        self.max_samples = sample_rate * max_duration_sec
        self.buffer = np.array([], dtype='float32')

    def append(self, chunk):
        """Appends a new chunk to the buffer. Converts int16 to float32 if needed."""
        if chunk.dtype == 'int16':
            chunk = chunk.astype('float32') / 32768.0
        
        # Ensure it's 1D
        chunk = chunk.flatten()
        
        self.buffer = np.append(self.buffer, chunk)
        
        # Maintain window size
        if len(self.buffer) > self.max_samples:
            self.buffer = self.buffer[-self.max_samples:]

    def get_all(self):
        """Returns the entire buffer as a float32 array."""
        return self.buffer

    def get_last_n_seconds(self, seconds):
        """Returns the last N seconds of audio."""
        n_samples = int(self.sample_rate * seconds)
        return self.buffer[-n_samples:]

    def clear(self):
        """Clears the buffer."""
        self.buffer = np.array([], dtype='float32')

    def __len__(self):
        return len(self.buffer)
