import sys, os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                          QLabel, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt
from auth import LoginWorker, get_user_info
from ui_helper import CustomErrorDialog
from key_manager import KeyManager

# HomePage class that handles login and displays user details
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SafeDrive')
        # Much larger initial window size
        self.setFixedSize(800, 700)
        self.setup_ui()
        self.move(250, 50)
        
        
    def setup_ui(self):
        # Set dark theme palette
        self.set_dark_theme()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 60, 60, 60)
        main_layout.setSpacing(30)
        
        # App logo and title section
        logo_layout = QVBoxLayout()
        
        # App title with gradient text
        title_label = QLabel("SafeDrive")
        title_label.setFont(QFont('Segoe UI', 48, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            background: transparent;
            color: #4285F4;
        """)
        
        # Subtitle
        subtitle_label = QLabel("Secure Google Drive Management")
        subtitle_label.setFont(QFont('Segoe UI', 18))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("background: transparent; color: #BBBBBB; margin-bottom: 10px;")
        
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        logo_layout.addSpacing(40)
        
        # Welcome message with subtle glow
        welcome_label = QLabel("Welcome to SafeDrive")
        welcome_label.setFont(QFont('Segoe UI', 24, QFont.Weight.Medium))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            background: transparent;
            color: #FFFFFF;
        """)
        
        # Description
        description_label = QLabel("Your documents, media, and files securely managed in one place.")
        description_label.setFont(QFont('Segoe UI', 16))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet("background: transparent; color: #AAAAAA;")
        description_label.setWordWrap(True)
        
        # Container for login button
        login_container = QFrame()
        login_container.setMinimumHeight(120)
        login_container.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(20, 20, 20, 20)
        
        # Google Drive login button
        self.google_button = QPushButton()
        self.google_button.setFixedSize(400, 60)
        self.google_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.google_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5294FF;
            }
            QPushButton:pressed {
                background-color: #3275E5;
            }
        """)
        
        # Create a horizontal layout for the button content
        button_content = QHBoxLayout()
        button_content.setContentsMargins(20, 0, 20, 0)
        button_content.setSpacing(15)
        
        # Google logo
        google_logo = QLabel()
        pixmap = QPixmap("Icon/google_logo.png")  # Make sure this path is correct
        pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        google_logo.setPixmap(pixmap)
        google_logo.setFixedSize(30, 30)
        google_logo.setStyleSheet("""background: transparent; padding: 0px; margin: 0px;""")

        
        # Button text
        button_text = QLabel("Continue with Google Drive")
        button_text.setFont(QFont('Segoe UI', 16, QFont.Weight.Medium))
        button_text.setStyleSheet("""
            color: white;
            background: transparent;
            padding: 0px;
            margin: 0px;
        """)
        
        # Add content to button layout
        button_content.addWidget(google_logo)
        button_content.addWidget(button_text)
        button_content.addStretch()
        
        # Set the layout for the button
        self.google_button.setLayout(button_content)
        self.google_button.clicked.connect(self.login_user)
        
        # Add button with proper spacing
        button_container = QHBoxLayout()
        button_container.addStretch(1)
        button_container.addWidget(self.google_button)
        button_container.addStretch(1)
        login_layout.addLayout(button_container)
        
        # Add elements to main layout
        main_layout.addLayout(logo_layout)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(description_label)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        main_layout.addWidget(login_container)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Footer
        footer_label = QLabel("© 2025 SafeDrive")
        footer_label.setFont(QFont('Segoe UI', 10))
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("background: transparent; color: #777777;")
        main_layout.addWidget(footer_label)
        
        self.setLayout(main_layout)
    
    def set_dark_theme(self):
        # Set dark theme for the entire application
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(25, 25, 28))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 50))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 60))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Set stylesheet for the entire widget
        self.setStyleSheet("""
            QWidget {
                background-color: #19191C;
                color: #FFFFFF;
            }
        """)
    
    def show_login_error(self, message: str):
        dialog = CustomErrorDialog(message, self)
        dialog.exec()
    def login_user(self):
        self.login_worker = LoginWorker()
        self.login_worker.login_success.connect(self.on_login_success)
        self.login_worker.login_failed.connect(self.show_login_error)
        self.login_worker.start()
    def on_login_success(self, creds):
        user_details = get_user_info(creds)
        if creds and creds.valid:
            email = user_details["email"]
            self.key_manager = KeyManager(email, parent=self)
            if not self.key_manager.enc_umk:
                retry = QMessageBox.question(
                    self,
                    "Key Not Found",
                    "No valid key was found or registration was cancelled.\nWould you like to retry?",
                    QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Close
                )
                if retry == QMessageBox.StandardButton.Retry:
                    self.key_manager = KeyManager(email, parent=self)
                    if not self.key_manager.enc_umk:
                        QMessageBox.critical(self, "Aborted", "Key still not available. Exiting.")
                        sys.exit()
                    else:
                        sys.exit()
        self.parent().show_main_page(creds, self.key_manager.enc_umk)