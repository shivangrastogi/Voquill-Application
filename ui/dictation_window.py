import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WaveformWidget(QWidget):
    """Animated waveform widget that reacts to audio volume."""
    def __init__(self):
        super().__init__()
        self.level = 0.0
        self.phase = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(30) # ~33 FPS

    def set_amplitude(self, value):
        """Adds a new amplitude value to the waveform."""
        self.level = float(np.clip(value, 0.0, 1.0))

    def _tick(self):
        # Right-to-left wave travel
        self.phase -= 0.22
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center_y = h / 2
        x_vals = np.linspace(0, w, 60)
        amp = 0.20 + (self.level * 0.55)

        # Three layered waves (sin/cos/tan) for a DNA-like motion
        sin_y = center_y + np.sin((x_vals / 19.0) + self.phase) * (h * amp * 0.45)
        cos_y = center_y + np.cos((x_vals / 16.0) + (self.phase * 1.3)) * (h * amp * 0.35)
        tan_component = np.tan((x_vals / 42.0) + (self.phase * 0.6))
        tan_component = np.clip(tan_component, -1.0, 1.0)
        tan_y = center_y + tan_component * (h * amp * 0.18)

        # Draw crossing connectors for the DNA feel
        connector_pen = QPen(QColor(55, 90, 140, 120), 1)
        painter.setPen(connector_pen)
        for i in range(0, len(x_vals), 4):
            painter.drawLine(int(x_vals[i]), int(sin_y[i]), int(x_vals[i]), int(cos_y[i]))

        sin_path = QPainterPath()
        cos_path = QPainterPath()
        tan_path = QPainterPath()
        sin_path.moveTo(0, sin_y[0])
        cos_path.moveTo(0, cos_y[0])
        tan_path.moveTo(0, tan_y[0])
        for i in range(1, len(x_vals)):
            sin_path.lineTo(x_vals[i], sin_y[i])
            cos_path.lineTo(x_vals[i], cos_y[i])
            tan_path.lineTo(x_vals[i], tan_y[i])

        painter.setPen(QPen(QColor(40, 140, 255), 2))
        painter.drawPath(sin_path)
        painter.setPen(QPen(QColor(125, 200, 255), 2))
        painter.drawPath(cos_path)
        painter.setPen(QPen(QColor(200, 235, 255, 170), 1))
        painter.drawPath(tan_path)

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
        self.current_state = "inactive"
        self.is_clicked = False
        self.init_ui()
        self._dragging = False
        self._drag_pos = None
        self._press_pos = QPoint()

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

        # 0. State Header (Always visible)
        self.state_widget = QWidget()
        state_layout = QHBoxLayout(self.state_widget)
        state_layout.setContentsMargins(0, 0, 0, 0)
        state_layout.setSpacing(6)
        self.state_dot = QLabel("●")
        self.state_dot.setStyleSheet("font-size: 10px; color: #777;")
        self.state_label = QLabel("Inactive")
        self.state_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #8a8a8a;")
        state_layout.addWidget(self.state_dot)
        state_layout.addWidget(self.state_label)
        state_layout.addStretch()

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

        self.container_layout.addWidget(self.state_widget)
        self.container_layout.addWidget(self.mode_widget)
        self.container_layout.addWidget(self.waveform)
        self.container_layout.addWidget(self.status_label)
        
        self.root_layout.addWidget(self.container)
        self.setFixedSize(140, 60) # Initial collapsed size

    def update_style(self, expanded):
        """Updates the styling of the main container."""
        radius = 18 if expanded else 12
        palette = {
            "inactive": ("#121212" if expanded else "#0a0a0a", "#333" if expanded else "#1a1a1a"),
            "listening": ("#0f1622", "#1e88e5"),
            "processing": ("#1a130f", "#d9822b"),
        }
        bg, border = palette.get(self.current_state, palette["inactive"])
        if self.is_clicked:
            border = "#6a6aff" if self.current_state == "inactive" else border
        
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
            self._press_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        # Treat minimal movement as click and toggle accent style
        if (event.globalPos() - self._press_pos).manhattanLength() < 5:
            self.is_clicked = not self.is_clicked
            self.update_style(self.is_expanded)

    def update_status(self, text):
        self.status_label.setText(text)
    
    def set_state(self, state):
        state = (state or "inactive").lower()
        self.current_state = state
        if state == "listening":
            self.state_dot.setStyleSheet("font-size: 10px; color: #1e88e5;")
            self.state_label.setText("Active")
            self.state_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #8dc3ff;")
        elif state == "processing":
            self.state_dot.setStyleSheet("font-size: 10px; color: #d9822b;")
            self.state_label.setText("Processing")
            self.state_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #ffc37a;")
        else:
            self.state_dot.setStyleSheet("font-size: 10px; color: #777;")
            self.state_label.setText("Inactive")
            self.state_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #8a8a8a;")

        self.update_style(self.is_expanded)

    def update_mode(self, mode):
        if mode in self.modes:
            self.current_mode_idx = self.modes.index(mode)
            self.mode_label.setText(mode)

    def set_wave_level(self, value):
        self.waveform.set_amplitude(value)

    def show_idle_bar(self):
        """Show small horizontal bar above taskbar."""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.collapse()
            self.set_state("inactive")
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + geo.height() - self.height() - 10
            self.move(x, y)
        self.show()
        self.raise_()
