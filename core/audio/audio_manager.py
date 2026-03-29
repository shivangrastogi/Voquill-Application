import sounddevice as sd
import numpy as np
import queue
import sys

class AudioManager:
    """Captures real-time audio streams in 20ms chunks."""
    
    def __init__(self, sample_rate=16000, channels=1, chunk_duration_ms=20):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_recording = False

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(f"Audio Status: {status}", file=sys.stderr)
        self.audio_queue.put(indata.copy())

    def start_streaming(self):
        """Starts the microphone stream."""
        if self.stream is not None:
            return

        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=self.channels,
            dtype='int16',
            callback=self._callback
        )
        self.stream.start()
        print("Audio Streaming Started...")

    def stop_streaming(self):
        """Stops the microphone stream."""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Audio Streaming Stopped.")

    def get_chunk(self):
        """Retrieves a single chunk from the queue (blocking)."""
        try:
            return self.audio_queue.get(timeout=1)
        except queue.Empty:
            return None

    def clear_queue(self):
        """Clears any pending audio chunks."""
        while not self.audio_queue.empty():
            self.audio_queue.get()
