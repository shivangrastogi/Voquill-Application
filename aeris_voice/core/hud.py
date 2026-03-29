import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

class HUDSignals(QObject):
    update_text = pyqtSignal(str)
    update_status = pyqtSignal(str)

class AetherHUD(QWidget):
    """A minimal, translucent, non-intrusive HUD for AetherVoice."""
    
    def __init__(self):
        super().__init__()
        self.signals = HUDSignals()
        self.init_ui()
        
    def init_ui(self):
        # Window Flags: Frameless, Always on Top, Non-Focusable
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Layout
        layout = QVBoxLayout()
        self.status_label = QLabel("Inactive")
        self.status_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background-color: rgba(50, 50, 50, 200); padding: 5px; border-radius: 5px;")
        
        self.text_label = QLabel("")
        self.text_label.setStyleSheet("color: #00ff00; font-size: 12px; font-style: italic; background-color: rgba(30, 30, 30, 150); padding: 5px; border-radius: 5px;")
        self.text_label.setWordWrap(True)
        self.text_label.hide()
        
        layout.addWidget(self.status_label, alignment=Qt.AlignRight)
        layout.addWidget(self.text_label, alignment=Qt.AlignRight)
        self.setLayout(layout)
        
        # Position (Bottom Right)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 350, screen.height() - 150, 300, 100)
        
        # Signal Connections
        self.signals.update_status.connect(self._set_status)
        self.signals.update_text.connect(self._set_text)

    def _set_status(self, text):
        self.status_label.setText(text)
        if text == "Inactive":
            self.status_label.setStyleSheet("color: #aaaaaa; background-color: rgba(50, 50, 50, 200); padding: 5px; border-radius: 5px;")
            self.text_label.hide()
        elif text == "Listening":
            self.status_label.setStyleSheet("color: #00ccff; background-color: rgba(0, 50, 80, 220); padding: 5px; border-radius: 5px;")
        elif text == "Recording...":
            self.status_label.setStyleSheet("color: #ff3333; background-color: rgba(80, 0, 0, 220); padding: 5px; border-radius: 5px;")

    def _set_text(self, text):
        if text:
            self.text_label.setText(text)
            self.text_label.show()
        else:
            self.text_label.hide()

def run_hud(hud_signal_target):
    """Entry point for HUD thread."""
    app = QApplication(sys.argv)
    hud = AetherHUD()
    # Link signs
    hud_signal_target['status'] = hud.signals.update_status
    hud_signal_target['text'] = hud.signals.update_text
    hud.show()
    sys.exit(app.exec_())
