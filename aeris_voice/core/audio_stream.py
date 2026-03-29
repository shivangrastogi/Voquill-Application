import sounddevice as sd
import numpy as np
import queue

# Global queue for audio chunks
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Sounddevice callback to put audio into the queue."""
    if status:
        print(f"Audio Status: {status}")
    q.put(indata.copy())

def start_stream():
    """Starts the audio input stream and returns the stream object."""
    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        callback=audio_callback,
        blocksize=8000 # 500ms at 16k
    )
    stream.start()
    return stream
