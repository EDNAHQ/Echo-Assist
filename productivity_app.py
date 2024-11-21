import sys
import os
import ctypes
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QFrame, QComboBox, QMessageBox,
                           QPushButton, QSlider, QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QScreen

# Import our modules
from modules.style_config import ThemeConfig
from modules.custom_title_bar import CustomTitleBar
from modules.voice_typer import VoiceTyperWidget
from modules.avatar_chat import AvatarChatWidget
from modules.screenshot import ScreenshotWidget
from avatars.avatar_configs import AVATARS

class ProductivityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Remove window frame and set up theme
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.theme = ThemeConfig()
        self.current_size = self.theme.sizes["window"]
        self.setMinimumSize(300, 400)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Echo Assist')
        self.resize(self.current_size)
        
        # Position window in the top-left corner
        self.move(0, 0)
        
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add custom title bar
        self.title_bar = CustomTitleBar(self, "🎯 Echo Assist")
        main_layout.addWidget(self.title_bar)
        
        # Create content container
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(4)
        
        # Create sidebar and content
        self.sidebar = self.create_sidebar()
        content_frame = self.create_content_area()
        
        # Add widgets to content layout
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(content_frame)
        
        # Add content container to main layout
        main_layout.addWidget(content_container)
        
        # Set window style
        self.update_styles()

    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(4, 4, 4, 4)
        sidebar_layout.setSpacing(4)
        
        # Create navigation buttons
        nav_buttons = [
            ("💬 Chat Assistant", 0),
            ("⌨️ Voice Typer", 1),
            ("📸 Screenshot Analysis", 2),  # New button for screenshot analysis
            ("⚙️ Settings", 3)
        ]
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFont(self.theme.SMALL_FONT)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        return sidebar

    def create_content_area(self):
        """Create the main content area with stacked widgets"""
        content_frame = QFrame()
        content_frame.setObjectName("content")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget to hold different pages
        self.stack = QStackedWidget()
        
        # Create and add pages
        self.avatar_chat = AvatarChatWidget(self.theme, AVATARS)
        self.voice_typer = VoiceTyperWidget(self.theme)
        self.screenshot_widget = ScreenshotWidget(self.theme)  # New screenshot widget
        self.settings_widget = self.create_settings_widget()  # Add settings widget back
        
        self.stack.addWidget(self.avatar_chat)
        self.stack.addWidget(self.voice_typer)
        self.stack.addWidget(self.screenshot_widget)  # Add screenshot widget to stack
        self.stack.addWidget(self.settings_widget)  # Add settings widget to stack
        
        content_layout.addWidget(self.stack)
        return content_frame

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def change_avatar(self, avatar_name):
        """Update the current avatar and its voice"""
        if avatar_name in AVATARS:
            self.avatar_chat.set_avatar(avatar_name)

    def change_theme(self, theme_name):
        """Update application theme"""
        self.theme.current_theme = theme_name
        self.update_styles()
        
    def resize_window(self, width):
        """Resize the window while maintaining aspect ratio"""
        current_ratio = self.height() / self.width()
        new_height = int(width * current_ratio)
        self.resize(width, new_height)

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.current_size = self.theme.sizes["window"]
        self.resize(self.current_size)
        self.theme_combo.setCurrentText("Dark")
        self.update_styles()

    def toggle_settings(self):
        """Toggle settings panel visibility"""
        current_index = self.settings_stack.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.settings_stack.setCurrentIndex(new_index)
        
        # Update button text
        settings_btn = self.findChild(QPushButton, "settings-btn")
        if settings_btn:
            settings_btn.setText("⚙ Settings" if new_index == 1 else "⚙ Hide Settings")

    def update_styles(self):
        """Update styles for all components"""
        # Update title bar
        self.title_bar.update_theme()
        
        # Update main application styles
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.theme.get_color('primary')},
                    stop:1 {self.theme.get_color('primary_gradient')});
            }}
            QLabel {{
                color: {self.theme.get_color('text')};
                font-size: 13px;
                padding: 5px;
                background: transparent;
            }}
            #sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('secondary')},
                    stop:1 {self.theme.get_color('secondary_gradient')});
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 10px;
                margin: 10px;
            }}
            #content {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('secondary')},
                    stop:1 {self.theme.get_color('secondary_gradient')});
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 10px;
            }}
            QComboBox, QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('secondary')},
                    stop:1 {self.theme.get_color('secondary_gradient')});
                color: {self.theme.get_color('text')};
                border: 1px solid {self.theme.get_color('border')};
                border-radius: 6px;
                padding: 8px;
                min-height: 20px;
            }}
            QComboBox:hover, QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('hover')},
                    stop:1 {self.theme.get_color('secondary_gradient')});
                border: 1px solid {self.theme.get_color('accent')};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('accent')},
                    stop:1 {self.theme.get_color('accent_gradient')});
            }}
            QPushButton[selected=true] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.theme.get_color('accent')},
                    stop:1 {self.theme.get_color('accent_gradient')});
                border: 1px solid {self.theme.get_color('accent')};
            }}
            QSlider::groove:horizontal {{
                background: {self.theme.get_color('secondary_gradient')};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.theme.get_color('accent')};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {self.theme.get_color('accent_gradient')};
            }}
            #settings-btn {{
                text-align: left;
            }}
            QFrame#modes-frame {{
                background: transparent;
                border: none;
            }}
        """)

    def create_settings_widget(self):
        """Create the settings panel with window size and theme controls"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(8)

        # Window size control
        size_label = QLabel("Window Size")
        size_label.setFont(self.theme.SMALL_FONT)
        settings_layout.addWidget(size_label)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(300)
        size_slider.setMaximum(800)
        size_slider.setValue(self.width())
        size_slider.valueChanged.connect(self.resize_window)
        settings_layout.addWidget(size_slider)

        # Theme selection
        theme_label = QLabel("Theme")
        theme_label.setFont(self.theme.SMALL_FONT)
        settings_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setFont(self.theme.SMALL_FONT)
        settings_layout.addWidget(self.theme_combo)

        # Avatar selection
        avatar_label = QLabel("Chat Assistant")
        avatar_label.setFont(self.theme.SMALL_FONT)
        settings_layout.addWidget(avatar_label)

        avatar_combo = QComboBox()
        avatar_combo.addItems(['Joe', 'Ashley', 'Brian'])  # Explicitly list the avatars in order
        avatar_combo.setCurrentText('Joe')  # Set default to Joe
        avatar_combo.currentTextChanged.connect(self.change_avatar)
        avatar_combo.setFont(self.theme.SMALL_FONT)
        settings_layout.addWidget(avatar_combo)

        # Add stretch to push everything to the top
        settings_layout.addStretch()

        return settings_widget

def exception_hook(exctype, value, tb):
    """Global exception handler to prevent app from crashing silently"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print('Error:', error_msg)  # Print to console
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("An error occurred")
    msg.setInformativeText(str(value))
    msg.setDetailedText(error_msg)
    msg.setWindowTitle("Error")
    msg.exec()
    # Keep the default exception hook behavior
    sys.__excepthook__(exctype, value, tb)

if __name__ == '__main__':
    # Install global exception handler
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    try:
        ex = ProductivityApp()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting app: {e}")
        traceback.print_exc()
