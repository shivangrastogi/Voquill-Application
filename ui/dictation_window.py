import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WaveformWidget(QWidget):
    """Animated waveform widget that reacts to audio volume."""
    def __init__(self):
        super().__init__()
        self.amplitudes = np.zeros(40)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30) # ~33 FPS

    def set_amplitude(self, value):
        """Adds a new amplitude value to the waveform."""
        self.amplitudes = np.roll(self.amplitudes, -1)
        self.amplitudes[-1] = value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(0, 120, 215), 2) # Nice blue
        painter.setPen(pen)
        
        w = self.width()
        h = self.height()
        center_y = h / 2
        step = w / len(self.amplitudes)
        
        for i, amp in enumerate(self.amplitudes):
            x = i * step
            # Scale amplitude for visualization
            height = amp * (h * 0.8)
            painter.drawLine(
                int(x), int(center_y - height/2),
                int(x), int(center_y + height/2)
            )

class DictationWindow(QWidget):
    """Floating, frameless dictation window with collapsed and expanded states."""
    
    # Custom signals for UI-thread safe updates
    state_changed = pyqtSignal(str)
    mode_requested = pyqtSignal(int) # -1 for prev, 1 for next

    def __init__(self):
        super().__init__()
        self.modes = ["Polished", "Email", "Formal", "Professional", "Casual", "Verbatim"]
        self.current_mode_idx = 0
        self.is_expanded = False
        self.init_ui()
        self._dragging = False
        self._drag_pos = None

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(10, 10, 10, 10) # Padding for shadow/glow effect
        
        # UI Container (The Pill)
        self.container = QFrame()
        self.container.setObjectName("MainFrame")
        self.update_style(expanded=False)
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(15, 8, 15, 8)
        self.container_layout.setSpacing(5)

        # 1. Mode Selector (Visible in Expanded State)
        self.mode_widget = QWidget()
        mode_layout = QHBoxLayout(self.mode_widget)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_btn = QPushButton(" < ")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.setStyleSheet("QPushButton { color: #555; background: transparent; border: none; font-size: 16px; font-weight: bold; } QPushButton:hover { color: #0078d7; }")
        self.prev_btn.clicked.connect(lambda: self.change_mode(-1))
        
        self.mode_label = QLabel(self.modes[self.current_mode_idx])
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: bold;")
        
        self.next_btn = QPushButton(" > ")
        self.next_btn.setFixedWidth(30)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(lambda: self.change_mode(1))
        
        mode_layout.addWidget(self.prev_btn)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.next_btn)
        self.mode_widget.hide() # Hidden by default
        
        # 2. Waveform / Vertical Line
        self.waveform = WaveformWidget()
        self.waveform.setFixedHeight(24)
        
        # 3. Status Label (Visible in Expanded State)
        self.status_label = QLabel("Click to dictate")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        self.status_label.hide() # Hidden by default

        self.container_layout.addWidget(self.mode_widget)
        self.container_layout.addWidget(self.waveform)
        self.container_layout.addWidget(self.status_label)
        
        self.root_layout.addWidget(self.container)
        self.setFixedSize(140, 60) # Initial collapsed size

    def update_style(self, expanded):
        """Updates the styling of the main container."""
        radius = 18 if expanded else 12
        bg = "#121212" if expanded else "#0a0a0a"
        border = "#333" if expanded else "#1a1a1a"
        
        self.container.setStyleSheet(f"""
            QFrame#MainFrame {{
                background-color: {bg};
                border: 1.5px solid {border};
                border-radius: {radius}px;
            }}
        """)

    def enterEvent(self, event):
        """Expand on hover."""
        if not self.is_expanded:
            self.expand()

    def leaveEvent(self, event):
        """Collapse when mouse leaves."""
        # Don't collapse if we are actively listening
        if self.is_expanded:
            self.collapse()

    def expand(self):
        self.is_expanded = True
        self.setFixedSize(220, 100)
        self.mode_widget.show()
        self.status_label.show()
        self.waveform.setFixedHeight(30)
        self.update_style(expanded=True)

    def collapse(self):
        self.is_expanded = False
        self.setFixedSize(140, 60)
        self.mode_widget.hide()
        self.status_label.hide()
        self.waveform.setFixedHeight(24)
        self.update_style(expanded=False)

    def change_mode(self, delta):
        self.current_mode_idx = (self.current_mode_idx + delta) % len(self.modes)
        mode_name = self.modes[self.current_mode_idx]
        self.mode_label.setText(mode_name)
        self.mode_requested.emit(delta)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def update_status(self, text):
        self.status_label.setText(text)

    def update_mode(self, mode):
        if mode in self.modes:
            self.current_mode_idx = self.modes.index(mode)
            self.mode_label.setText(mode)

    def set_wave_level(self, value):
        self.waveform.set_amplitude(value)
