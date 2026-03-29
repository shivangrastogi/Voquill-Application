from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QLabel, QPushButton, QButtonGroup, 
                             QStackedWidget, QProgressBar, QListWidget, 
                             QLineEdit, QCheckBox, QApplication, QSpacerItem, 
                             QSizePolicy, QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QMetaObject, pyqtSlot, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QColor, QPainter, QPen, QFont, QPixmap, QLinearGradient, QPainterPath
from PyQt5 import QtSvg

class SVGIconWidget(QWidget):
    """Premium SVG renderer for white monochrome icons."""
    def __init__(self, path_data, size=32):
        super().__init__()
        self.setFixedSize(size, size)
        self.renderer = QtSvg.QSvgRenderer()
        # Wrap path in proper SVG boilerplate for white color
        svg_full = f'<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{path_data}</svg>'
        self.renderer.load(svg_full.encode('utf-8'))

    def paintEvent(self, event):
        painter = QPainter(self)
        self.renderer.render(painter)

class ICON_PATHS:
    HOME = '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>'
    HISTORY = '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
    DICTIONARY = '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'
    STYLES = '<circle cx="12" cy="12" r="3"/><path d="M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18zM12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>'
    SETTINGS = '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>'
    ROCKET = '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.71-2.12.71-2.12s-1.28 0-2.12.71z"/><path d="M15 3s-9 2-10 10c0 1.5 1 2.5 1 2.5s1 1 2.5 1c8-1 10-10 10-10l-3.5-3.5z"/>'
    MIC = '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>'
    AUDIO = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>'
    KEYBOARD = '<rect x="2" y="5" width="20" height="14" rx="2" ry="2"/><line x1="6" y1="8" x2="6.01" y2="8"/><line x1="10" y1="8" x2="10.01" y2="8"/><line x1="14" y1="8" x2="14.01" y2="8"/><line x1="18" y1="8" x2="18.01" y2="8"/><line x1="6" y1="12" x2="6.01" y2="12"/><line x1="18" y1="12" x2="18.01" y2="12"/><line x1="10" y1="12" x2="10.01" y2="12"/><line x1="14" y1="12" x2="14.01" y2="12"/><line x1="8" y1="16" x2="16" y2="16"/>'
    DIAGS = '<polyline points="18 13 12 7 8 11 2 5"/><polyline points="12 14 12 21"/><polyline points="16 21 16 14"/><polyline points="8 21 8 14"/><polyline points="4 21 4 14"/>'
    DISCORD = '<path d="M17.22 5.03C15.93 4.4 14.54 3.96 13.08 3.74c-.18.32-.38.74-.53 1.1-1.56-.23-3.1-.23-4.62 0-.15-.36-.36-.78-.54-1.1-1.46.22-2.85.66-4.14 1.29-2.61 3.89-3.32 7.69-2.97 11.43 1.73 1.27 3.41 2.05 5.04 2.56.41-.56.77-1.16 1.07-1.79-.59-.22-1.14-.5-1.67-.84.14-.1.28-.21.41-.33 3.27 1.51 6.81 1.51 10.02 0 .13.12.27.23.41.33-.53.34-1.08.62-1.67.84.3.63.66 1.23 1.07 1.79 1.63-.51 3.31-1.29 5.04-2.56.42-4.33-.71-8.09-2.97-11.43zM8.53 14.88c-.96 0-1.75-.88-1.75-1.97s.76-1.97 1.75-1.97s1.75.88 1.75 1.97s-.76 1.97-1.75 1.97zm6.94 0c-.96 0-1.75-.88-1.75-1.97s.76-1.97 1.75-1.97s1.75.88 1.75 1.97s-.76 1.97-1.75 1.97z"/>'
    EDGE = '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 18c-3.314 0-6-2.686-6-6s2.686-6 6-6 6 2.686 6 6-2.686 6-6 6z"/>'
    AERIS = '<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>'
    MIN = '<line x1="5" y1="12" x2="19" y2="12"/>'
    MAX = '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>'
    CLOSE = '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'

class CustomTitleBar(QFrame):
    """Premium custom title bar for frameless window."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #0d0d0d; border-bottom: 1px solid #1a1a1a;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        # App Icon and Name
        self.icon_widget = SVGIconWidget(ICON_PATHS.HOME, 18)
        self.title_label = QLabel("Voquill")
        self.title_label.setStyleSheet("color: #fff; font-size: 13px; font-weight: 800;")
        
        layout.addWidget(self.icon_widget)
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # Window Controls
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(30,30)
        self.min_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: #222; border-radius: 4px; }")
        self.min_icon = SVGIconWidget(ICON_PATHS.MIN, 14)
        min_l = QVBoxLayout(self.min_btn)
        min_l.setContentsMargins(8,8,8,8)
        min_l.addWidget(self.min_icon)
        self.min_btn.clicked.connect(self.parent.showMinimized)

        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(30,30)
        self.max_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: #222; border-radius: 4px; }")
        self.max_icon = SVGIconWidget(ICON_PATHS.MAX, 12)
        max_l = QVBoxLayout(self.max_btn)
        max_l.setContentsMargins(9,9,9,9)
        max_l.addWidget(self.max_icon)
        self.max_btn.clicked.connect(self.toggle_maximized)

        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(30,30)
        self.close_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: #c42b1c; border-radius: 4px; }")
        self.close_icon = SVGIconWidget(ICON_PATHS.CLOSE, 14)
        close_l = QVBoxLayout(self.close_btn)
        close_l.setContentsMargins(8,8,8,8)
        close_l.addWidget(self.close_icon)
        self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def toggle_maximized(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

class NavButton(QPushButton):
    """Custom sidebar navigation button with premium styling."""
    def __init__(self, text, icon_path="", active=False):
        super().__init__()
        self.active = active
        self.text_label = text
        self.icon_path = icon_path
        self.setFixedHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()
        self.update_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(12)
        
        self.icon_widget = SVGIconWidget(self.icon_path, 32)
        self.label = QLabel(self.text_label)
        self.label.setStyleSheet("font-size: 32px; font-weight: 700; color: inherit; background: transparent;")
        
        layout.addWidget(self.icon_widget)
        layout.addWidget(self.label)
        layout.addStretch()

    def update_style(self):
        bg = "#222" if self.active else "transparent"
        color = "#fff" if self.active else "#888"
        weight = "bold" if self.active else "normal"
        
        self.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {bg}; 
                border-radius: 12px; 
                border: none; 
            }}
            QPushButton:hover {{ 
                background-color: #1a1a1a; 
            }}
        """)
        self.label.setStyleSheet(f"color: {color}; font-weight: {weight}; font-size: 32px; background: transparent;")
        # Icons remain white for the premium look per user request
        pass

class StatCard(QFrame):
    """Premium Card for displaying statistics."""
    def __init__(self, title, value, icon_text="", color="#ff6b35"):
        super().__init__()
        self.setFixedSize(220, 160)
        self.setObjectName("StatCardFrame")
        self.setStyleSheet(f"""
            QFrame#StatCardFrame {{
                background-color: #161616;
                border: 1.5px solid #252525;
                border-radius: 16px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Value Area (Horizontal if icon exists)
        val_lay = QHBoxLayout()
        val_lay.setSpacing(10)
        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
            val_lay.addWidget(icon_label)
            
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #fff; font-size: 52px; font-weight: 950;")
        val_lay.addWidget(self.value_label)
        val_lay.addStretch()
        layout.addLayout(val_lay)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #777; font-size: 15px; font-weight: 700;")
        layout.addWidget(self.title_label)

class DashboardWindow(QMainWindow):
    """Main application dashboard."""
    word_added = pyqtSignal(str, object) # word, replacement (can be None)
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Voquill")
        self.resize(1200, 850)
        self.current_user = "Shivang"
        
        # Outer Shell for the entire window to allow custom title bar placement
        self.outer_widget = QWidget()
        self.outer_widget.setObjectName("OuterShell")
        self.outer_widget.setStyleSheet("QWidget#OuterShell { background-color: #0d0d0d; border: 1px solid #1a1a1a; }")
        self.setCentralWidget(self.outer_widget)
        
        self.outer_layout = QVBoxLayout(self.outer_widget)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        self.outer_layout.addWidget(self.title_bar)

        # 2. Main Content Area
        self.main_container = QWidget()
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.outer_layout.addWidget(self.main_container)
        
        self.init_sidebar()
        self.init_content()
        
    def update_stats(self, stats):
        """Updates the dynamic statistics on the home page."""
        if hasattr(self, 'streak_card'):
            self.streak_card.value_label.setText(str(stats.get('streak', 0)))
        if hasattr(self, 'month_words_card'):
            self.month_words_card.value_label.setText(str(stats.get('month_words', 0)))
        if hasattr(self, 'total_words_card'):
            self.total_words_card.value_label.setText(str(stats.get('total_words', 0)))

    def paintEvent(self, event):
        """Draws a subtle dot grid background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(40, 40, 40)) # Very subtle dots
        
        gap = 25
        for x in range(0, self.width(), gap):
            for y in range(0, self.height(), gap):
                painter.drawPoint(x, y)

    def init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QFrame { 
                background-color: #0d0d0d; 
                border-right: 1px solid #1a1a1a;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        # Logo with Accent
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(10, 10, 10, 20)
        self.logo_widget = SVGIconWidget(ICON_PATHS.HOME, 32)
        logo_text = QLabel("Voquill")
        logo_text.setStyleSheet("color: #fff; font-size: 28px; font-weight: 900; background: transparent;")
        logo_layout.addWidget(self.logo_widget)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)
        
        # Navigation
        self.nav_group = QButtonGroup(self)
        self.nav_home = NavButton("Home", ICON_PATHS.HOME, active=True)
        self.nav_history = NavButton("History", ICON_PATHS.HISTORY)
        self.nav_dict = NavButton("Dictionary", ICON_PATHS.DICTIONARY)
        self.nav_styles = NavButton("Styles", ICON_PATHS.STYLES)
        
        sidebar_layout.addWidget(self.nav_home)
        sidebar_layout.addWidget(self.nav_history)
        sidebar_layout.addWidget(self.nav_dict)
        sidebar_layout.addWidget(self.nav_styles)
        
        sidebar_layout.addStretch()
        
        # No status widgets per user request

        # Version Footer
        version_lbl = QLabel("v0.0.484")
        version_lbl.setStyleSheet("color: #444; font-size: 11px; font-weight: 600; margin-left: 20px; margin-bottom: 5px;")
        sidebar_layout.addWidget(version_lbl)

        # Settings button at bottom
        self.settings_btn = NavButton("Settings", ICON_PATHS.SETTINGS)
        sidebar_layout.addWidget(self.settings_btn)
        
        self.main_layout.addWidget(self.sidebar)

    def init_content(self):
        self.content_container = QWidget()
        self.content_container_layout = QVBoxLayout(self.content_container)
        self.content_container_layout.setContentsMargins(0, 0, 0, 0)
        self.content_container_layout.setSpacing(0)
        self.main_layout.addWidget(self.content_container)

        # 1. Global TopBar
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet("background-color: #0d0d0d; border-bottom: 1px solid #1a1a1a;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(35, 0, 35, 0)
        top_layout.addStretch()
        
        # Emptied top-right widgets per user request
        
        self.content_container_layout.addWidget(self.top_bar)

        # 2. Content Stack
        self.content_stack = QStackedWidget()
        self.content_container_layout.addWidget(self.content_stack)
        
        # --- HOME PAGE ---
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        home_layout.setContentsMargins(50, 40, 50, 40)
        home_layout.setSpacing(15)
        
        # Welcome Message
        self.welcome_label = QLabel(f"Welcome back, {self.current_user}")
        self.welcome_label.setStyleSheet("color: #fff; font-size: 74px; font-weight: 950; background: transparent;")
        sub_info = QLabel("Press Ctrl + Win to dictate anywhere.")
        sub_info.setStyleSheet("color: #777; font-size: 24px; font-weight: 600; background: transparent; margin-bottom: 10px;")
        home_layout.addWidget(self.welcome_label)
        home_layout.addWidget(sub_info)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.streak_card = StatCard("Day streak", "2", "🔥", "#ff8c00")
        stats_layout.addWidget(self.streak_card)
        self.month_words_card = StatCard("Words this month", "327")
        self.total_words_card = StatCard("Words total", "327")
        stats_layout.addWidget(self.month_words_card)
        stats_layout.addWidget(self.total_words_card)
        stats_layout.addStretch()
        home_layout.addLayout(stats_layout)
        
        # Detailed WPM View
        wpm_outer = QFrame()
        wpm_outer.setFixedHeight(95)
        wpm_outer.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1.5px solid #333;
                border-radius: 20px;
            }
        """)
        wpm_lay = QHBoxLayout(wpm_outer)
        wpm_lay.setContentsMargins(25, 0, 25, 0)
        wpm_val = QLabel("74 WPM")
        # Balanced 10% reduction from giant 48px -> ~43px
        wpm_val.setStyleSheet("color: #fff; font-size: 43px; font-weight: 950; background: transparent;")
        wpm_diff = QLabel("1.9x faster than typing")
        wpm_diff.setStyleSheet("color: #aaa; background: #333; border-radius: 12px; padding: 6px 15px; font-size: 18px; font-weight: 600; margin-left: 20px;")
        wpm_lay.addWidget(wpm_val)
        wpm_lay.addWidget(wpm_diff)
        wpm_lay.addStretch()
        home_layout.addWidget(wpm_outer)
        
        # Getting Started
        gs_header = QHBoxLayout()
        gs_header.setContentsMargins(0, 20, 0, 0)
        gs_label = QLabel("Getting started")
        gs_label.setStyleSheet("color: #fff; font-size: 29px; font-weight: 850;")
        gs_skip = QLabel("Skip")
        gs_skip.setStyleSheet("color: #555; font-size: 17px; font-weight: 600; margin-left: 12px;")
        gs_prg_label = QLabel("2 of 3")
        gs_prg_label.setStyleSheet("color: #555; font-size: 17px; font-weight: 800;")
        gs_header.addWidget(gs_label)
        gs_header.addWidget(gs_skip)
        gs_header.addStretch()
        gs_header.addWidget(gs_prg_label)
        home_layout.addLayout(gs_header)
        
        # Progress Bar
        pb = QProgressBar()
        pb.setFixedHeight(10)
        pb.setValue(66)
        pb.setTextVisible(False)
        pb.setStyleSheet("QProgressBar { background: #222; border-radius: 5px; border: none; } QProgressBar::chunk { background: #0078d7; border-radius: 5px; }")
        home_layout.addWidget(pb)
        
        # Checklist Items
        for i, (txt, done) in enumerate([("Use Voquill in 3 different apps", True), ("Select a different writing style", True), ("Add a word to your dictionary", False)]):
            cl_item = QWidget()
            cl_item.setFixedHeight(45)
            cl_lay = QHBoxLayout(cl_item)
            cl_lay.setContentsMargins(0, 5, 0, 5)
            cl_icon = QLabel("✔" if done else "○")
            cl_icon.setStyleSheet(f"color: {'#1E88E5' if done else '#444'}; font-size: 20px;")
            cl_text = QLabel(txt)
            cl_text.setStyleSheet(f"color: {'#fff' if done else '#777'}; font-size: 17px; font-weight: 600; margin-left: 10px;")
            cl_lay.addWidget(cl_icon)
            cl_lay.addWidget(cl_text)
            
            if i == 0:
                # Add App Icons from screenshot
                app_box = QHBoxLayout()
                app_box.setSpacing(8)
                app_box.setContentsMargins(15, 0, 0, 0)
                for ico in [ICON_PATHS.DISCORD, ICON_PATHS.AERIS, ICON_PATHS.EDGE]:
                    i_w = SVGIconWidget(ico, 20)
                    i_w.setStyleSheet("background: #1a1a1a; border-radius: 4px; border: 1px solid #333;")
                    app_box.addWidget(i_w)
                cl_lay.addLayout(app_box)
            
            cl_lay.addStretch()
            info_ico = QLabel("ⓘ")
            info_ico.setStyleSheet("color: #555; font-size: 18px;")
            cl_lay.addWidget(info_ico)
            home_layout.addWidget(cl_item)

        home_layout.addSpacing(30)
        # Recent Transcriptions Header with thick underline
        hist_header = QWidget()
        hh_lay = QVBoxLayout(hist_header)
        hh_lay.setContentsMargins(0, 0, 0, 0)
        hh_lay.setSpacing(5)
        hh_label = QLabel("Recent transcriptions")
        hh_label.setStyleSheet("color: #fff; font-size: 24px; font-weight: 900; background: transparent;")
        hh_line = QFrame()
        hh_line.setFixedWidth(160)
        hh_line.setFixedHeight(3)
        hh_line.setStyleSheet("background-color: #555; border: none; border-radius: 1.5px;")
        hh_lay.addWidget(hh_label)
        hh_lay.addWidget(hh_line)
        home_layout.addWidget(hist_header)
        
        home_layout.addStretch()
        self.content_stack.addWidget(home_page)
        
        # 2. History Page (Index 1)
        self.history_page = QWidget()
        hist_layout = QVBoxLayout(self.history_page)
        hist_title = QLabel("Recent transcriptions")
        hist_title.setStyleSheet("color: #fff; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        hist_layout.addWidget(hist_title)
        self.hist_list = QListWidget()
        self.hist_list.setStyleSheet("QListWidget { background-color: transparent; border: none; color: #ddd; font-size: 14px; } QListWidget::item { background-color: #1a1a1a; border-radius: 8px; padding: 10px; margin-bottom: 5px; } QListWidget::item:selected { background-color: #333; }")
        hist_layout.addWidget(self.hist_list)
        self.content_stack.addWidget(self.history_page)
        
        # 3. Dictionary Page (Same to Same Redesign)
        self.dict_page = QWidget()
        dict_layout = QVBoxLayout(self.dict_page)
        dict_layout.setContentsMargins(60, 40, 60, 40)
        dict_layout.setSpacing(15)
        
        d_header = QHBoxLayout()
        d_title = QLabel("Dictionary")
        d_title.setStyleSheet("color: #fff; font-size: 58px; font-weight: 950;")
        d_add = QPushButton("+ Add")
        d_add.setStyleSheet("background: transparent; color: #fff; font-size: 26px; font-weight: 800; border: none;")
        d_add.setCursor(Qt.PointingHandCursor)
        d_add.clicked.connect(self.on_add_word)
        d_header.addWidget(d_title)
        d_header.addStretch()
        d_header.addWidget(d_add)
        dict_layout.addLayout(d_header)
        
        d_desc = QLabel("Voquill may misunderstand you on occasion...")
        d_desc.setWordWrap(True)
        d_desc.setStyleSheet("color: #aaa; font-size: 20px; font-weight: 500; line-height: 1.6; margin-top: 10px;")
        dict_layout.addWidget(d_desc)
        
        # Dictionary List (Functional)
        self.dict_list = QListWidget()
        self.dict_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: #eee; font-size: 18px; }
            QListWidget::item { background: #1a1a1a; border-radius: 12px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; }
        """)
        dict_layout.addWidget(self.dict_list)
        
        # Inputs (Hidden by default, reveal on + Add)
        self.add_box = QFrame()
        self.add_box.setVisible(False)
        self.add_box.setStyleSheet("background: #111; border-radius: 15px; border: 1px solid #333;")
        ab_lay = QHBoxLayout(self.add_box)
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Original word")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replacement")
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.on_save_new_word)
        ab_lay.addWidget(self.word_input)
        ab_lay.addWidget(self.replace_input)
        ab_lay.addWidget(save_btn)
        dict_layout.addWidget(self.add_box)
        
        # Empty State
        self.empty_widget = QWidget()
        empty_vbox = QVBoxLayout(self.empty_widget)
        empty_title = QLabel("It's quiet in here")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_title.setStyleSheet("color: #fff; font-size: 32px; font-weight: 850;")
        empty_desc = QLabel("There are no items to display.")
        empty_desc.setAlignment(Qt.AlignCenter)
        empty_desc.setStyleSheet("color: #777; font-size: 19px; font-weight: 600;")
        empty_vbox.addWidget(empty_title)
        empty_vbox.addWidget(empty_desc)
        dict_layout.addWidget(self.empty_widget)
        
        dict_layout.addStretch(2)
        
        self.content_stack.addWidget(self.dict_page)
        
        # Styles/History Placeholders
        self.content_stack.addWidget(QLabel("History Page (Planned)"))
        self.content_stack.addWidget(QLabel("Styles Page (Planned)"))

        # 4. Styles Page (Index 3)
        self.styles_page = QWidget()
        styles_layout = QVBoxLayout(self.styles_page)
        styles_layout.addWidget(QLabel("Writing Styles Coming Soon..."))
        self.content_stack.addWidget(self.styles_page)
        
        # 5. Settings Page (Modern High-Fidelity)
        self.settings_page = QWidget()
        set_layout = QVBoxLayout(self.settings_page)
        set_layout.setContentsMargins(40, 30, 40, 30)
        
        set_title = QLabel("Settings")
        set_title.setStyleSheet("color: #fff; font-size: 72px; font-weight: 900; margin-bottom: 40px;")
        set_layout.addWidget(set_title)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        def add_section_header(title):
            lbl = QLabel(title)
            lbl.setStyleSheet("color: #fff; font-size: 22px; font-weight: 700; margin-top: 20px; margin-bottom: 15px;")
            scroll_layout.addWidget(lbl)

        def add_setting_row(text, icon_path="", has_toggle=False):
            row = QFrame()
            row.setFixedHeight(70)
            row.setStyleSheet("background-color: #121212; border-radius: 20px; border: 1.5px solid #222;")
            h_layout = QHBoxLayout(row)
            h_layout.setContentsMargins(20, 0, 20, 0)
            
            icon_widget = SVGIconWidget(icon_path, 32)
            label = QLabel(text)
            label.setStyleSheet("color: #eee; font-size: 24px; font-weight: 500; border: none; margin-left: 20px;")
            
            h_layout.addWidget(icon_widget)
            h_layout.addWidget(label)
            h_layout.addStretch()
            
            if has_toggle:
                toggle = QCheckBox()
                toggle.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 45px;
                        height: 24px;
                    }
                    QCheckBox::indicator:unchecked {
                        image: url(none); border: 2px solid #444; border-radius: 12px; background: #222;
                    }
                    QCheckBox::indicator:checked {
                        image: url(none); border: 2px solid #0078d7; border-radius: 12px; background: #0078d7;
                    }
                """)
                h_layout.addWidget(toggle)
            else:
                arrow = QLabel("⋮")
                arrow.setStyleSheet("color: #666; font-size: 20px; border: none;")
                h_layout.addWidget(arrow)
            
            scroll_layout.addWidget(row)

        add_section_header("General")
        add_setting_row("Start on system startup", ICON_PATHS.ROCKET, True)
        add_setting_row("Microphone", ICON_PATHS.MIC)
        add_setting_row("Audio", ICON_PATHS.AUDIO)
        add_setting_row("Hotkey shortcuts", ICON_PATHS.KEYBOARD)
        add_setting_row("Diagnostics", ICON_PATHS.DIAGS)
        add_setting_row("App paste bindings", ICON_PATHS.KEYBOARD)
        add_setting_row("More settings", ICON_PATHS.SETTINGS)

        add_section_header("Processing")
        processing_desc = QLabel("How Voquill should manage your transcriptions.")
        processing_desc.setStyleSheet("color: #777; font-size: 14px; margin-bottom: 10px;")
        scroll_layout.addWidget(processing_desc)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        set_layout.addWidget(scroll_area)
        self.content_stack.addWidget(self.settings_page)
        
        # Connect Buttons
        self.nav_home.clicked.connect(lambda: self.switch_page(0))
        self.nav_history.clicked.connect(lambda: self.switch_page(1))
        self.nav_dict.clicked.connect(lambda: self.switch_page(2))
        self.nav_styles.clicked.connect(lambda: self.switch_page(3))
        self.settings_btn.clicked.connect(lambda: self.switch_page(4))

    def on_add_word(self):
        self.add_box.setVisible(not self.add_box.isVisible())

    def on_save_new_word(self):
        word = self.word_input.text().strip()
        replacement = self.replace_input.text().strip()
        if word:
            self.word_added.emit(word, replacement if replacement else None)
            self.word_input.clear()
            self.replace_input.clear()
            self.add_box.setVisible(False)
            self.refresh_dictionary(self.current_dict if hasattr(self, 'current_dict') else [])

    def on_logout_click(self):
        self.logout_requested.emit()

    def update_user_info(self, user):
        """No longer used in auth-free version."""
        pass

    def logout(self):
        self.hide()

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        self.sidebar.setVisible(True)
        buttons = [self.nav_home, self.nav_history, self.nav_dict, self.nav_styles, self.settings_btn]
        for i, btn in enumerate(buttons):
            btn.active = (i == index) 
            btn.update_style()

    def refresh_history(self, history_data):
        self.hist_list.clear()
        for item in history_data:
            # item schema: (id, ts, raw, clean, mode, app_context)
            ts = item[1][:16].replace('T', ' ')
            clean_text = item[3]
            app = item[5] if len(item) > 5 else "Unknown"
            
            # Limit character length for display
            display_text = clean_text[:60] + "..." if len(clean_text) > 60 else clean_text
            self.hist_list.addItem(f"[{ts}] [{app}] {display_text}")

    def refresh_dictionary(self, entries):
        self.dict_list.clear()
        # entries expects list of words or dict map
        if isinstance(entries, dict):
            for word, replacement in entries.items():
                self.dict_list.addItem(f"{word} → {replacement}")
        else:
            for word in entries:
                self.dict_list.addItem(word)
