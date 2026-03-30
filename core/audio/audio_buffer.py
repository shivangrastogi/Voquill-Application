from collections import deque
import numpy as np

class AudioBuffer:
    """Manages a sliding window of audio data."""
    
    def __init__(self, sample_rate=16000, max_duration_sec=30):
        self.sample_rate = sample_rate
        self.max_samples = sample_rate * max_duration_sec
        self._chunks = deque()
        self._chunk_sizes = deque()
        self._total_samples = 0

    def append(self, chunk):
        """Appends a new chunk to the buffer. Converts int16 to float32 if needed."""
        if chunk.dtype == 'int16':
            chunk = chunk.astype('float32') / 32768.0
        
        # Ensure it's 1D
        chunk = chunk.flatten()
        if chunk.size == 0:
            return

        self._chunks.append(chunk)
        self._chunk_sizes.append(chunk.size)
        self._total_samples += chunk.size

        # Maintain window size without full-array copies each append
        while self._total_samples > self.max_samples and self._chunks:
            removed = self._chunks.popleft()
            removed_size = self._chunk_sizes.popleft()
            self._total_samples -= removed_size
            # Keep only tail of the removed chunk if needed
            overflow = self.max_samples - self._total_samples
            if overflow > 0 and removed_size > overflow:
                tail = removed[-overflow:]
                self._chunks.appendleft(tail)
                self._chunk_sizes.appendleft(tail.size)
                self._total_samples += tail.size

    def get_all(self):
        """Returns the entire buffer as a float32 array."""
        if not self._chunks:
            return np.array([], dtype='float32')
        return np.concatenate(self._chunks).astype('float32', copy=False)

    def get_last_n_seconds(self, seconds):
        """Returns the last N seconds of audio."""
        n_samples = int(self.sample_rate * seconds)
        if n_samples <= 0 or not self._chunks:
            return np.array([], dtype='float32')
        if self._total_samples <= n_samples:
            return self.get_all()
        return self.get_all()[-n_samples:]

    def clear(self):
        """Clears the buffer."""
        self._chunks.clear()
        self._chunk_sizes.clear()
        self._total_samples = 0

    def __len__(self):
        return self._total_samples
