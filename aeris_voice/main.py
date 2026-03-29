import numpy as np
import threading
import queue
import shutil
import time
import sys
import yaml
import os

from core.audio_stream import start_stream, q
from core.stt_stream import STT
from core.vad import VADProcessor
from core.injector import KeyboardInjector
from core.hotkey import HotkeyListener
from core.context import WindowTracker
from core.transcript_manager import TranscriptManager
from core.ai_cleaner import AICleaner
from core.hud import run_hud, HUDSignals, AetherHUD
from utils.logger import setup_logger
import signal
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def handle_exit():
    print("\n[AetherVoice] Shutting down gracefully...")
    # This will trigger the app.exec_() to return or clean up
    QApplication.quit()

class AetherVoiceApp:
    def __init__(self, hud_signals):
        self.hud_signals = hud_signals
        self.config = self._load_config()
        self.logger = setup_logger(log_level=self.config['ai']['log_level'])
        
        try:
            self.logger.info("Initializing STT Engine...")
            self.stt = STT(
                model_size=self.config['stt']['model_size'],
                compute_type=self.config['stt']['compute_type']
            )
            
            self.logger.info("Initializing VAD Engine...")
            self.vad = VADProcessor(threshold=self.config['vad']['threshold'])
            
            self.injector = KeyboardInjector()
            self.tracker = WindowTracker()
            self.manager = TranscriptManager()
            
            self.ai = None
            if self.config['ai']['enabled']:
                self.logger.info(f"Initializing AI Cleaner ({self.config['ai']['provider']})...")
                self.ai = AICleaner(
                    provider=self.config['ai']['provider'],
                    model=self.config['ai']['model'],
                    api_key=self.config['ai']['api_key']
                )
                
        except Exception as e:
            self.logger.error(f"Critical System Initialization Failure: {e}")
            raise

        self.is_listening = False
        self.is_speaking = False
        self.silence_timer = 0
        self.speech_buffer = []
        self.segment_id = 0
        self.stream = None # Hardware stream object

    def _load_config(self):
        default = {
            'stt': {'model_size': 'base', 'compute_type': 'int8'},
            'vad': {'threshold': 0.5, 'hangover_time': 0.8, 'min_speech_len': 0.5},
            'ai': {'enabled': True, 'model': 'mistral', 'timeout': 3.0, 'async_overwrite': True, 'log_level': 'INFO'},
            'system': {'hotkey': '<ctrl>+<cmd>', 'typing_delay': 0.002}
        }
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r") as f:
                cfg = yaml.safe_load(f)
                for key in default:
                    if key not in cfg: cfg[key] = default[key]
                return cfg
        return default

    def on_toggle(self, active):
        self.is_listening = active
        if self.is_listening:
            # Clear old audio data from the queue
            while not q.empty():
                try: q.get_nowait()
                except queue.Empty: break
            
            # 1. Open and Start Microsoft
            try:
                self.stream = start_stream()
                self.tracker.lock_current_window()
                self._update_hud_status("Listening")
                self.logger.info(f"Dictation Started. Mic Active. Target: {self.tracker.target_title}")
            except Exception as e:
                self.logger.error(f"Could not open microphone: {e}")
                self.is_listening = False
                return

        else:
            # 2. Stop and Release Microsoft
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                    self.stream = None
                except Exception as e:
                    self.logger.error(f"Error closing microphone: {e}")

            # When toggled OFF, process whatever we have in the buffer (Manual Mode)
            if self.is_speaking or self.speech_buffer:
                self.logger.info("Hotkey pressed: Finalizing dictation...")
                self._update_hud_status("Polishing...")
                self._process_segment_complete()
            
            self.is_speaking = False
            self.speech_buffer = []
            self.silence_timer = 0
            self._update_hud_status("Inactive")
            self.logger.info("Dictation Stopped. Mic Released.")

    def _update_hud_status(self, status):
        if 'status' in self.hud_signals:
            self.hud_signals['status'].emit(status)

    def _update_hud_text(self, text):
        if 'text' in self.hud_signals:
            self.hud_signals['text'].emit(text)

    def voice_loop(self):
        """Background loop for audio processing."""
        print("\n[AetherVoice] System Ready.")
        print(f">>> Press {self.config['system']['hotkey']} to Toggle Dictation <<<\n")
        
        hotkey = HotkeyListener(
            toggle_key=self.config['system']['hotkey'],
            callback=self.on_toggle
        )
        hotkey.start()
        
        try:
            while True:
                if not self.is_listening:
                    time.sleep(0.1)
                    continue

                try:
                    # Chunks are only pushed to q when stream is running (see audio_stream.py)
                    chunk = q.get(timeout=2.0)
                    audio_chunk = chunk.flatten().astype("float32")
                    
                    if self.vad.is_speech(audio_chunk):
                        if not self.is_speaking:
                            self.is_speaking = True
                            self._update_hud_status("Recording...")
                        
                        self.speech_buffer.append(audio_chunk)
                        self.silence_timer = 0
                    else:
                        if self.is_speaking:
                            self.speech_buffer.append(audio_chunk)
                            self.silence_timer += 0.5 
                            
                            if self.silence_timer >= 10.0:
                                self._process_segment_complete()
                                self.speech_buffer = []
                                self.is_speaking = False
                                self.silence_timer = 0
                                
                except queue.Empty:
                    continue
        except Exception as e:
            self.logger.error(f"Voice Loop Fatal Error: {e}")

    def _process_segment_complete(self):
        self.segment_id += 1
        curr_id = self.segment_id
        
        if not self.speech_buffer:
            return

        full_audio = np.concatenate(self.speech_buffer)
        
        # Reset buffer immediately to allow for next segment
        self.speech_buffer = [] 
        
        # 1. Raw Fast STT
        raw_text = self.stt.transcribe(full_audio).strip()
        if not raw_text:
            return

        if self.tracker.is_target_active():
            # Use paste_text for instant injection (All-at-once)
            self.injector.paste_text(raw_text + " ")
            self.manager.add_segment(raw_text)
            self._update_hud_text(raw_text)
            self.logger.info(f"Segment #{curr_id} [RAW]: {raw_text}")
            
            if self.ai and self.config['ai']['async_overwrite']:
                threading.Thread(
                    target=self._async_ai_polish, 
                    args=(raw_text, curr_id, self.manager.get_context(limit=3)),
                    daemon=True
                ).start()
        else:
            self.logger.warning("Focus changed; injection blocked.")

    def _async_ai_polish(self, raw_text, target_id, context):
        try:
            polished = self.ai.polish(raw_text, context=context, timeout=self.config['ai']['timeout'])
            if polished and polished != raw_text and target_id == self.segment_id:
                if self.tracker.is_target_active():
                    self.logger.info(f"Segment #{target_id} [FIX]: {polished}")
                    undo_str = "\b" * (len(raw_text) + 1)
                    self.injector.type_text(undo_str + polished + " ", delay_per_char=0)
                    self._update_hud_text(f"✨ {polished}")
                    self.manager.add_segment(polished)
        except Exception as e:
            self.logger.error(f"AI Polish Error: {e}")

if __name__ == "__main__":
    # 1. Handle Ctrl+C in terminal
    signal.signal(signal.SIGINT, lambda *args: handle_exit())

    # Force UTF-8 for Windows Console
    try:
        if sys.platform == "win32":
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except Exception:
        pass

    # Main Thread MUST own the QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 2. Setup HUD
    hud = AetherHUD()
    hud.show()
    
    # 3. Setup System Tray
    tray_icon = QSystemTrayIcon(app)
    # Using a standard system icon as a placeholder (Computer Icon)
    tray_icon.setIcon(app.style().standardIcon(app.style().SP_ComputerIcon))
    
    menu = QMenu()
    show_action = QAction("Show HUD", menu)
    show_action.triggered.connect(hud.show)
    hide_action = QAction("Hide HUD", menu)
    hide_action.triggered.connect(hud.hide)
    quit_action = QAction("Quit AetherVoice", menu)
    quit_action.triggered.connect(handle_exit)
    
    menu.addAction(show_action)
    menu.addAction(hide_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    tray_icon.setToolTip("AetherVoice AI Assistant")
    
    hud_signals = {
        'status': hud.signals.update_status,
        'text': hud.signals.update_text
    }
    
    try:
        voice_app = AetherVoiceApp(hud_signals)
        threading.Thread(target=voice_app.voice_loop, daemon=True).start()
        
        # Start the event loop
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application failed to start: {e}")
