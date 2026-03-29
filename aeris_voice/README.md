# 🎙️ AetherVoice: Professional Local-First AI Voice Assistant

AetherVoice is a high-performance, private, and unlimited voice-to-text system for Windows. It uses **Faster-Whisper** for local transcription and a **Win32 Clipboard-Paste** mechanism for instant, zero-latency text injection into any application.

---

## 🏗️ System Architecture & Logic (AI-Optimized)

### 1. Data Flow Pipeline
1.  **Trigger**: User presses the global hotkey (`ctrl+windows` by default).
2.  **Hardware Access**: `main.py` calls `audio_stream.py` to open the microphone stream dynamically.
3.  **VAD Gating**: `core/vad.py` (Silero VAD) monitors the stream. If speech is detected, chunks are added to the `speech_buffer`.
4.  **Manual Stop**: User presses the hotkey again. The stream is closed immediately, releasing the hardware.
5.  **Transcription**: `core/stt_stream.py` processes the recorded buffer using `faster-whisper`.
6.  **Injection**: `core/injector.py` copies the text to the Windows Clipboard via `ctypes` and sends a hardware-level `Ctrl+V` command.

### 2. Concurrency Model
-   **Main Thread**: Owns the `PyQt5` event loop and the System Tray icon. 
-   **Voice Loop (Daemon Thread)**: Handles the blocking audio queue and VAD logic to keep the UI responsive.
-   **AI Thread (Optional)**: If cloud polishing is enabled, a one-off thread performs the API call and "Undo-Swap" injection.

---

## 📂 Structural Module Breakdown

### `main.py` (The Orchestrator)
- **Role**: Coordinates all modules and manages the application lifecycle.
- **Logic**: 
    - Initializes STT, VAD, Injector, and HUD.
    - Manages `is_listening` (mic toggle) and `is_speaking` (VAD) states.
    - Handles graceful shutdown via `QSystemTrayIcon` and `SIGINT`.

### `core/audio_stream.py` (Hardware Layer)
- **Role**: Low-level audio capture using `sounddevice`.
- **Logic**: Returns a stream object that can be started/stopped manually to ensure the microphone isn't "always on".

### `core/stt_stream.py` (The Brain)
- **Role**: Local Speech-to-Text via `faster-whisper`.
- **Logic**: Loads models (e.g., `small`, `base`) in `int8` quantization for high performance on CPUs.

### `core/vad.py` (The Filter)
- **Role**: Voice Activity Detection via `silero-vad`.
- **Logic**: Sub-chunks incoming 16kHz audio into 512-sample blocks to satisfy Silero's strict requirements.

### `core/injector.py` (The Output)
- **Role**: System-wide text injection.
- **Logic**: Uses `ctypes` to access Win32 API (`user32.dll` and `kernel32.dll`). 
    - `paste_text()`: Copies UTF-16 text to the clipboard and simulates `Ctrl+V`.

### `core/hotkey.py` (The Input)
- **Role**: Global hotkey listener using the `keyboard` library.
- **Logic**: Intercepts keys even when the app is minimized.

### `core/hud.py` (The Interface)
- **Role**: Semi-transparent, "Always-on-top" status indicator.

---

## 🛠️ Installation & Requirements

### Dependencies
- `faster-whisper`: High-speed local transcription.
- `silero-vad`: Zero-latency voice detection.
- `PyQt5`: GUI and System Tray.
- `sounddevice`: Microphone access.
- `keyboard`: Global hotkey interception.

### Configuration (`config.yaml`)
- `stt.model_size`: Set to `small` for high accuracy or `base` for speed.
- `system.hotkey`: Default is `ctrl+windows`.
- `ai.enabled`: Toggle for optional cloud polishing (Groq/HuggingFace).

---

## 🚀 Recommended AI Prompt for ChatGPT/Claude
If you are giving this project to another AI, use this:
> "This is AetherVoice, a local Windows voice assistant. It uses a manual toggle via `ctrl+windows`. It captures audio only when active, transcribes it locally using Whisper, and then uses a Win32 clipboard paste to inject it. The entry point is `main.py`. Please analyze the `core/` folder to understand the threading and hardware management."

---
*Developed for AetherVoice: Private. Unlimited. Revolutionary.*
