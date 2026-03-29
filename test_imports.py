import sys
import os

print("Starting import check...")

try:
    import torch
    print(f"Torch version: {torch.__version__}")
except Exception as e:
    print(f"Torch import failed: {e}")

try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 import successful")
except Exception as e:
    print(f"PyQt5 import failed: {e}")

try:
    import faster_whisper
    print("faster-whisper import successful")
except Exception as e:
    print(f"faster-whisper import failed: {e}")

try:
    import ollama
    print("ollama import successful")
except Exception as e:
    print(f"ollama import failed: {e}")

try:
    import pygetwindow
    print("pygetwindow import successful")
except Exception as e:
    print(f"pygetwindow import failed: {e}")

print("Import check complete.")
