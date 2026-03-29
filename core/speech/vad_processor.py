import webrtcvad

class VADProcessor:
    """Detects voice activity in audio chunks to filter out silence."""
    
    def __init__(self, aggressiveness=3):
        """
        Aggressiveness: 0 (least filtering) to 3 (most aggressive).
        Mode 3 is best for suppressing background noise hallucinations.
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000

    def is_speech(self, audio_chunk):
        """
        Checks if an audio chunk contains speech.
        Expects audio_chunk as int16 1D numpy array or bytes.
        """
        # Convert to bytes if it's a numpy array
        if hasattr(audio_chunk, 'tobytes'):
            audio_bytes = audio_chunk.tobytes()
        else:
            audio_bytes = audio_chunk

        # webrtcvad requires 10, 20, or 30ms of audio
        # Our 20ms chunks are perfect for this
        try:
            return self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception as e:
            print(f"VAD Error: {e}")
            return False
