import os
import sqlite3
# Fix for WinError 1114: Import torch before PyQt5 and allow duplicate OpenMP libs
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
try:
    import torch
except ImportError:
    pass

import sys
import threading
import time
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QMetaObject, Qt, pyqtSlot

import pygetwindow as gw
from difflib import SequenceMatcher

# Core imports
from core.audio.audio_manager import AudioManager
from core.audio.audio_buffer import AudioBuffer
from core.speech.vad_processor import VADProcessor
from core.speech.transcriber import Transcriber
try:
    from core.ai.ai_cleaner import AICleaner
except ImportError:
    AICleaner = None

from core.injection.keyboard_controller import KeyboardController
from core.control.hotkey_listener import HotkeyListener
from core.control.session_manager import SessionManager, SessionState
from core.control.database_manager import DatabaseManager
from core.formatting.command_parser import CommandParser
from core.formatting.dictionary_engine import DictionaryEngine

# UI imports
from ui.dictation_window import DictationWindow
from ui.dashboard import DashboardWindow
from ui.tray_icon import TrayIcon

class VoquillApp(QObject):
    """Main application logic coordinating all components."""
    
    def __init__(self):
        super().__init__()
        
        # 1. Initialize Core
        self.db = DatabaseManager()
        self.audio_manager = AudioManager()
        self.audio_buffer = AudioBuffer()
        self.vad = VADProcessor()
        self.transcriber = Transcriber(model_size="base")
        self.ai_cleaner = AICleaner() if AICleaner else None
        self.injector = KeyboardController()
        self.session = SessionManager()
        self.parser = CommandParser()
        
        # Initialize Dictionary Engine
        dict_map = self.db.get_dictionary_map()
        self.dict_engine = DictionaryEngine(dict_map)
        
        # 2. Initialize UI
        self.dashboard = DashboardWindow()
        self.dashboard.word_added.connect(self.handle_word_added)
        self.dashboard.logout_requested.connect(self.handle_logout)
        
        self.window = DictationWindow()
        self.window.mode_requested.connect(self.handle_mode_cycle)
        self.tray = TrayIcon(on_show=self.show_dashboard, on_exit=self.quit_app)
        
        # 3. Setup Hotkey
        self.hotkey = HotkeyListener(callback=self.toggle_dictation)
        
        # 4. State
        self.is_listening = False
        self.app_context = "Unknown"

    def start(self):
        """Starts the application."""
        # Boot directly to dashboard (Auth removed as requested)
        self.show_dashboard()
        self.tray.start()
        self.hotkey.start()
        print("Voquill is running (Performance Mode)...")

    def handle_login(self, email, password):
        pass

    def handle_signup(self, email, password, name):
        pass

    def handle_mode_cycle(self, delta):
        modes = self.window.modes
        current_idx = self.window.current_mode_idx
        # sync mode to session
        self.session.set_mode(modes[current_idx])
        print(f"Mode Changed to: {modes[current_idx]}")

    def handle_word_added(self, word, replacement=None):
        self.db.add_word(word, replacement)
        # Refresh engine mapping
        self.dict_engine.update_dictionary(self.db.get_dictionary_map())

    def handle_logout(self):
        self.dashboard.hide()

    def show_dashboard(self):
        # Refresh data before showing
        history = self.db.get_history()
        words = self.db.get_dictionary()
        stats = self.db.get_usage_stats()
        
        self.dashboard.refresh_history(history)
        self.dashboard.refresh_dictionary(words)
        self.dashboard.update_stats(stats)
        
        self.dashboard.show()
        self.dashboard.raise_()

    def show_window(self):
        # The floating window is triggered by hotkey, not menu
        self.window.show()
        self.window.raise_()

    def toggle_dictation(self):
        """Main entry point for hotkey toggle."""
        if not self.is_listening:
            # We must use QTimer to call start_dictation from the UI thread 
            # because the hotkey listener runs in a background thread.
            QMetaObject.invokeMethod(self, "start_dictation", Qt.QueuedConnection)
        else:
            QMetaObject.invokeMethod(self, "stop_dictation", Qt.QueuedConnection)

    @pyqtSlot()
    def start_dictation(self):
        self.is_listening = True
        
        # Capture active window context
        try:
            active_window = gw.getActiveWindow()
            self.app_context = active_window.title if active_window else "Desktop"
        except:
            self.app_context = "Unknown"
        
        self.window.show()
        self.session.set_state(SessionState.LISTENING)
        self.audio_buffer.clear()
        self.audio_manager.start_streaming()
        self.window.update_status("Listening...")
        threading.Thread(target=self._stream_processing_loop, daemon=True).start()
        threading.Thread(target=self._transcription_loop, daemon=True).start()

    @pyqtSlot()
    def stop_dictation(self):
        self.is_listening = False
        self.audio_manager.stop_streaming()
        self.session.set_state(SessionState.PROCESSING)
        self.window.update_status("Processing AI...")
        threading.Thread(target=self._finalize_dictation, daemon=True).start()

    def _stream_processing_loop(self):
        """Real-time loop for VAD and waveforms."""
        print("Stream Processing Loop Started")
        chunks_received = 0
        chunks_accepted = 0
        while self.is_listening:
            chunk = self.audio_manager.get_chunk()
            if chunk is not None:
                chunks_received += 1
                # Update Waveform (UI-safe via set_wave_level in DictationWindow)
                rms = np.sqrt(np.mean(chunk.astype(float)**2))
                level = min(1.0, rms / 5000)
                self.window.set_wave_level(level)
                
                is_speech = self.vad.is_speech(chunk)
                if is_speech:
                    chunks_accepted += 1
                    self.audio_buffer.append(chunk)
                
                if chunks_received % 100 == 0:
                    print(f"Audio Stats - Chunks Received: {chunks_received}, Accepted (Speech): {chunks_accepted}, Current RMS: {rms:.2f}")

    def _transcription_loop(self):
        """Refined 2.0s window / 0.7s interval transcription loop with diff-based injection."""
        print("Transcription Loop Started")
        last_transcription_time = time.time()
        self.previous_full_transcript = ""
        self.last_speech_time = time.time()
        
        while self.is_listening:
            current_time = time.time()
            if current_time - last_transcription_time > 0.7:
                audio_data = self.audio_buffer.get_last_n_seconds(2.0)
                buffer_len = len(audio_data)
                
                if buffer_len > 3200:
                    max_val = np.max(np.abs(audio_data))
                    # Increased threshold to 0.02 to avoid hiss/background noise
                    if max_val > 0.02:
                        audio_data = audio_data / (max_val + 1e-6)
                        raw_text = self.transcriber.transcribe(audio_data)
                        
                        # Secondary check for single-word hallucinations not caught by Transcriber blacklist
                        if len(raw_text.split()) == 1 and raw_text.lower().strip(".,?!") in ["music", "thanks", "bye"]:
                            raw_text = ""
                        print(f"Raw Whisper Transcript: '{raw_text}'")
                        
                        # Apply Dictionary Replacements
                        processed_text = self.dict_engine.apply(raw_text)
                        
                        # Robust Injection: Inject only what's added to the end
                        new_words = processed_text.split()
                        old_words = self.previous_full_transcript.split()
                        
                        # Find common prefix length
                        common_len = 0
                        for o, n in zip(old_words, new_words):
                            # Robust comparison: ignore case and punctuation differences
                            if o.lower().strip(".,?!\"'") == n.lower().strip(".,?!\"'"):
                                common_len += 1
                            else:
                                break
                        
                        words_to_inject = new_words[common_len:]
                        if words_to_inject:
                            text_to_inject = " ".join(words_to_inject) + " "
                            self.injector.inject(text_to_inject)
                            self.previous_full_transcript = processed_text
                            self.last_speech_time = current_time
                            # Use encode/decode to avoid Windows console errors
                            safe_text = text_to_inject.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                            print(f"Streaming Inject: {safe_text}")
                        else:
                            print("No new words to inject (diff empty)")
                else:
                    if buffer_len > 0:
                        print(f"Buffer too small to transcribe: {buffer_len} samples")
                
                last_transcription_time = current_time
            time.sleep(0.05)

    def _finalize_dictation(self):
        """Final transcription check and async AI cleanup."""
        try:
            audio_data = self.audio_buffer.get_all()
            if len(audio_data) < 1600:
                self.window.update_status("Empty session")
                time.sleep(0.5)
                self.window.hide()
                return

            # Final transcription
            max_val = np.max(np.abs(audio_data))
            if max_val > 0: audio_data = audio_data / max_val
            
            raw_text = self.transcriber.transcribe(audio_data)
            processed_text = self.dict_engine.apply(raw_text)
            
            # Ensure anything missed by the 0.7s loop is typed
            final_words = processed_text.split()
            old_words = self.previous_full_transcript.split()
            
            common_len = 0
            for o, n in zip(old_words, final_words):
                if o.lower().strip(".,?!") == n.lower().strip(".,?!"):
                    common_len += 1
                else:
                    break
            
            words_to_inject = final_words[common_len:]
            if words_to_inject:
                text_to_inject = " ".join(words_to_inject)
                self.injector.inject(text_to_inject.strip())

            self.window.update_status("Polishing...")
            # Run AI Cleanup with App Context awareness
            if self.ai_cleaner:
                threading.Thread(target=self._run_async_cleanup, args=(processed_text,), daemon=True).start()
            else:
                self.db.add_history(processed_text, processed_text, self.session.get_mode(), self.app_context)
            
            self.window.update_status("Done!")
            time.sleep(0.5)
            self.window.hide()

        except Exception as e:
            print(f"Finalization Error: {e}")
            self.window.update_status("Error!")
            time.sleep(1)
            self.window.hide()

    def _run_async_cleanup(self, text):
        """Asynchronously polishes the full transcript and saves to history."""
        try:
            mode = self.session.get_mode()
            # Pass app_context to cleaner for potential context-aware polishing
            clean_text = self.ai_cleaner.clean(text, mode=mode)
            self.db.add_history(text, clean_text, mode, self.app_context)
            print(f"Async Cleanup Done for {self.app_context}: {clean_text[:50]}...")
        except Exception as e:
            print(f"Async Cleanup Error: {e}")

    def quit_app(self):
        self.hotkey.stop()
        self.audio_manager.stop_streaming()
        self.tray.stop()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    voquill = VoquillApp()
    voquill.start()
    sys.exit(app.exec_())
