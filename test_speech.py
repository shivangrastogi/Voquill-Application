from core.audio.audio_manager import AudioManager
from core.audio.audio_buffer import AudioBuffer
from core.speech.vad_processor import VADProcessor
from core.speech.transcriber import Transcriber
import time
import numpy as np

def test_speech_pipeline():
    print("--- Speech Pipeline Test (VAD + Whisper) ---")
    
    # 1. Init
    manager = AudioManager()
    buffer = AudioBuffer()
    vad = VADProcessor(aggressiveness=2)
    transcriber = Transcriber(model_size="base")
    
    # 2. Capture with VAD
    manager.start_streaming()
    print("Recording... Speak now (Hinglish test: 'Uh mujhe lagta hai we should start'). Stop in 5s.")
    
    start_time = time.time()
    speech_detected_count = 0
    total_chunks = 0
    
    while time.time() - start_time < 5:
        chunk = manager.get_chunk()
        if chunk is not None:
            total_chunks += 1
            if vad.is_speech(chunk):
                speech_detected_count += 1
                buffer.append(chunk)
    
    manager.stop_streaming()
    
    print(f"Total chunks processed: {total_chunks}")
    print(f"Speech chunks detected: {speech_detected_count}")
    
    # 3. Transcribe
    if len(buffer) > 0:
        print("Transcribing...")
        audio_data = buffer.get_all()
        result = transcriber.transcribe(audio_data)
        print(f"TRANSLATION RESULT: {result}")
    else:
        print("No speech detected. Skipping transcription.")

if __name__ == "__main__":
    test_speech_pipeline()
