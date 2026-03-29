from core.audio.audio_manager import AudioManager
from core.audio.audio_buffer import AudioBuffer
from core.audio.device_manager import DeviceManager
import time

def test_capture():
    print("--- Audio Capture Test ---")
    
    # 1. List devices
    devices = DeviceManager.list_input_devices()
    print(f"Available input devices: {len(devices)}")
    for d in devices:
        print(f" - [{d['index']}] {d['name']}")
    
    default = DeviceManager.get_default_input_device()
    print(f"Default Device: {default['name']}")

    # 2. Setup Manager and Buffer
    manager = AudioManager()
    buffer = AudioBuffer(max_duration_sec=10)
    
    # 3. Start Streaming
    manager.start_streaming()
    
    print("Recording for 3 seconds...")
    start_time = time.time()
    while time.time() - start_time < 3:
        chunk = manager.get_chunk()
        if chunk is not None:
            buffer.append(chunk)
    
    manager.stop_streaming()
    
    # 4. Results
    print(f"Buffer size: {len(buffer)} samples")
    print(f"Duration captured: {len(buffer)/16000:.2f} seconds")
    
    if len(buffer) > 0:
        print("SUCCESS: Audio data captured.")
    else:
        print("FAILURE: No audio data captured.")

if __name__ == "__main__":
    test_capture()
