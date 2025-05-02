from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QGraphicsDropShadowEffect, QLineEdit, QProgressBar, QCheckBox,
    QHeaderView, QLabel, QMenu, QAbstractItemView, QGraphicsOpacityEffect, QWidgetAction, QFrame, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt, QFile, QSize, QUrl, QPropertyAnimation, QEasingCurve, QEvent, QPointF, QObject
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainterPath, QFont, QPainter, QMovie, QPainter
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import re

class CustomErrorDialog(QDialog):
    def __init__(self, title, message: str, parent=None):
        super().__init__(parent)
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(420, 220)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with background
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)
        
        # Create container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Error icon - try GIF first, fallback to PNG, then to text
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        try:
            movie = QMovie("Icon/error.gif")
            if movie.isValid():
                icon_label.setMovie(movie)
                movie.start()
            else:
                raise Exception("Invalid GIF")
        except:
            pixmap = QPixmap("Icon/error.png") 
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                    Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                # If no image is found, display text instead
                icon_label.setText("⚠️")
                icon_label.setFont(QFont("Arial", 32))
                icon_label.setStyleSheet("color: #e74c3c; background: transparent;")
                
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 13px; color: #e0e0e0; background: transparent;")
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setMinimumHeight(40)
        ok_button.setMinimumWidth(100)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        # Add widgets to container layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(message_label)
        container_layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add container to main layout
        self.main_layout.addWidget(self.container)
        
    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class CustomSuccessDialog(QDialog):
    def __init__(self, title, message: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(620, 220)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container widget
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        # Layout for container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Success icon (animated or static fallback)
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        try:
            movie = QMovie("success.gif")
            if movie.isValid():
                icon_label.setMovie(movie)
                movie.start()
            else:
                raise Exception("Invalid GIF")
        except:
            pixmap = QPixmap("success.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("✅")
                icon_label.setFont(QFont("Arial", 32))
                icon_label.setStyleSheet("color: #2ecc71; background: transparent;")

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 10px; color: #e0e0e0; background: transparent;")

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setMinimumHeight(40)
        ok_button.setMinimumWidth(100)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        ok_button.clicked.connect(self.accept)

        # Assemble layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(message_label)
        container_layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.container)

    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class CustomMessageBox(QDialog):
    """Custom stylish message box with animations"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(420, 220)  # Match size with other dialogs
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with background
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)
        
        # Create container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Icon selection
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        try:
            movie = QMovie("question.gif")
            if movie.isValid():
                icon_label.setMovie(movie)
                movie.start()
            else:
                raise Exception("Invalid GIF")
        except:
            pixmap = QPixmap("question.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("❓")
                icon_label.setFont(QFont("Arial", 32))
                icon_label.setStyleSheet("color: #4C86D0; background: transparent;")                
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 13px; color: #e0e0e0; background: transparent;")
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # No button
        self.no_button = QPushButton("No")
        self.no_button.setMinimumHeight(40)
        self.no_button.setMinimumWidth(100)
        self.no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.no_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """)
        self.no_button.clicked.connect(lambda: self.done(QDialog.DialogCode.Rejected))
        
        # Yes button
        self.yes_button = QPushButton("Yes")
        self.yes_button.setMinimumHeight(40)
        self.yes_button.setMinimumWidth(100)
        self.yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #4C86D0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #5A9BE7;
            }
            QPushButton:pressed {
                background-color: #3C76C0;
            }
        """)
        self.yes_button.clicked.connect(lambda: self.done(QDialog.DialogCode.Accepted))
        
        button_layout.addWidget(self.no_button)
        button_layout.addWidget(self.yes_button)
        
        # Add widgets to container layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(message_label)
        container_layout.addLayout(button_layout)
        
        # Add container to main layout
        self.main_layout.addWidget(self.container)
        
    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class CustomEmailDialog(QDialog):
    def __init__(self, title="Share File", message="Enter email to share with:", parent=None):
        super().__init__(parent)
        self.email = ""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(420, 270)  # Slightly taller to accommodate input field

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container widget
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        # Layout for container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Share icon (email icon or static fallback)
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        try:
            movie = QMovie("email.gif")
            if movie.isValid():
                icon_label.setMovie(movie)
                movie.start()
            else:
                raise Exception("Invalid GIF")
        except:
            pixmap = QPixmap("email.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("📧")
                icon_label.setFont(QFont("Arial", 32))
                icon_label.setStyleSheet("color: #3498db; background: transparent;")

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 13px; color: #e0e0e0; background: transparent;")

        # Email input field
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(40)
        self.email_input.setPlaceholderText("example@email.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(40)
        cancel_button.setMinimumWidth(100)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        # OK button
        ok_button = QPushButton("Share")
        ok_button.setMinimumHeight(40)
        ok_button.setMinimumWidth(100)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        ok_button.clicked.connect(self.accept_input)

        # Add buttons to layout
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(ok_button)

        # Assemble layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(message_label)
        container_layout.addWidget(self.email_input)
        container_layout.addLayout(buttons_layout)

        self.main_layout.addWidget(self.container)
        
        # Set focus to the email input
        self.email_input.setFocus()

    def accept_input(self):
        self.email = self.email_input.text()
        self.accept()
        
    def get_email(self):
        return self.email

    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class CustomRenameDialog(QDialog):
    def __init__(self, title="Rename Item", message="Enter new name:", current_name="", parent=None):
        super().__init__(parent)
        self.new_name = ""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(420, 270)  # Similar size to email dialog

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container widget
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        # Layout for container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Rename icon
        icon_label = QLabel()
        icon_label.setStyleSheet("background: transparent;")
        try:
            movie = QMovie("rename.gif")
            if movie.isValid():
                icon_label.setMovie(movie)
                movie.start()
            else:
                raise Exception("Invalid GIF")
        except:
            pixmap = QPixmap("rename.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🔄")
                icon_label.setFont(QFont("Arial", 32))
                icon_label.setStyleSheet("color: #9b59b6; background: transparent;")

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 13px; color: #e0e0e0; background: transparent;")

        # Name input field
        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #9b59b6;
            }
        """)
        
        # Select all text when dialog opens
        self.name_input.selectAll()

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(40)
        cancel_button.setMinimumWidth(100)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        # Rename button
        rename_button = QPushButton("Rename")
        rename_button.setMinimumHeight(40)
        rename_button.setMinimumWidth(100)
        rename_button.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
        """)
        rename_button.clicked.connect(self.accept_input)

        # Add buttons to layout
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(rename_button)

        # Assemble layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(message_label)
        container_layout.addWidget(self.name_input)
        container_layout.addLayout(buttons_layout)

        self.main_layout.addWidget(self.container)
        
        # Set focus to the name input
        self.name_input.setFocus()

    def accept_input(self):
        self.new_name = self.name_input.text()
        self.accept()
        
    def get_new_name(self):
        return self.new_name

    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class PasswordDialog(QDialog):
    """Custom attractive password creation dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Secure Password")
        self.setFixedSize(650, 720)  # Increased size for better visibility
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with background
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)
        
        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel()
        icon = QIcon.fromTheme("security-high")
        if icon and not icon.isNull():
            pixmap = icon.pixmap(QSize(48, 48))
            icon_label.setPixmap(pixmap)
        else:
            # Fallback to text icon
            icon_label.setText("🔒")
            icon_label.setFont(QFont("Arial", 28))
            icon_label.setStyleSheet("color: #4C86D0;")
        
        # Title
        title_layout = QVBoxLayout()
        title_label = QLabel("Create Your Master Password")
        title_label.setObjectName("title_label")
        subtitle_label = QLabel("This password will protect all your encrypted data")
        subtitle_label.setObjectName("subtitle_label")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Warning message
        warning_frame = QFrame()
        warning_frame.setObjectName("warning_frame")
        warning_layout = QHBoxLayout(warning_frame)
        
        warning_icon = QLabel()
        warning_icon_theme = QIcon.fromTheme("dialog-warning")
        if warning_icon_theme and not warning_icon_theme.isNull():
            warning_pixmap = warning_icon_theme.pixmap(QSize(24, 24))
            warning_icon.setPixmap(warning_pixmap)
        else:
            # Fallback to text icon
            warning_icon.setText("⚠️")
            warning_icon.setFont(QFont("Arial", 18))
            warning_icon.setStyleSheet("color: #e74c3c;")
        
        warning_text = QLabel(
            "WARNING: Your password is NEVER stored anywhere.\n"
            "If you forget it, all your encrypted data will be permanently lost."
        )
        warning_text.setWordWrap(True)
        
        warning_layout.addWidget(warning_icon)
        warning_layout.addWidget(warning_text, 1)
        
        # Password and confirm fields
        password_layout = QVBoxLayout()
        
        # Password field with show/hide button
        password_label = QLabel("Password:")
        password_field_layout = QHBoxLayout()
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Enter your password")
        self.password_field.textChanged.connect(self.check_password_strength)
        self.password_field.setObjectName("password_field")
        self.password_field.setMinimumHeight(40)
        
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setIcon(QIcon("Icon/eye-off.png")) 
        self.toggle_password_btn.setObjectName("toggle_button")
        self.toggle_password_btn.setFixedSize(40, 40)
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.clicked.connect(lambda: self.toggle_password_visibility(self.password_field))
        
        password_field_layout.addWidget(self.password_field)
        password_field_layout.addWidget(self.toggle_password_btn)
        
        # Confirm password field with show/hide button
        confirm_label = QLabel("Confirm Password:")
        confirm_field_layout = QHBoxLayout()
        
        self.confirm_field = QLineEdit()
        self.confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_field.setPlaceholderText("Confirm your password")
        self.confirm_field.textChanged.connect(self.check_passwords_match)
        self.confirm_field.setObjectName("password_field")
        self.confirm_field.setMinimumHeight(40)
        
        self.toggle_confirm_btn = QPushButton()
        self.toggle_confirm_btn.setIcon(QIcon("Icon/eye-off.png")) 
        self.toggle_confirm_btn.setObjectName("toggle_button")
        self.toggle_confirm_btn.setFixedSize(40, 40)
        self.toggle_confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_confirm_btn.clicked.connect(lambda: self.toggle_password_visibility(self.confirm_field))
        
        confirm_field_layout.addWidget(self.confirm_field)
        confirm_field_layout.addWidget(self.toggle_confirm_btn)
        
        # Password strength indicators
        strength_layout = QHBoxLayout()
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(8)
        self.strength_bar.setObjectName("strength_bar")
        
        self.strength_label = QLabel("Password Strength: Too Weak")
        self.strength_label.setObjectName("strength_label")
        
        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.strength_label)
        
        # Password policy frame
        policy_frame = QFrame()
        policy_frame.setObjectName("policy_frame")
        policy_layout = QVBoxLayout(policy_frame)
        
        policy_title = QLabel("Password Requirements:")
        policy_title.setObjectName("policy_title")
        
        # Policy checklist
        self.length_check = QLabel("❌ At least 8 characters")
        self.uppercase_check = QLabel("❌ At least 1 uppercase letter")
        self.digit_check = QLabel("❌ At least 1 number")
        self.special_check = QLabel("❌ At least 1 special character")
        
        for label in [self.length_check, self.uppercase_check, self.digit_check, self.special_check]:
            label.setObjectName("policy_item")
        
        policy_layout.addWidget(policy_title)
        policy_layout.addWidget(self.length_check)
        policy_layout.addWidget(self.uppercase_check)
        policy_layout.addWidget(self.digit_check)
        policy_layout.addWidget(self.special_check)
        
        # Match indicator
        self.match_label = QLabel("")
        self.match_label.setObjectName("match_label")
        
        # Add password fields to layout
        password_layout.addWidget(password_label)
        password_layout.addLayout(password_field_layout)
        password_layout.addSpacing(5)
        password_layout.addLayout(strength_layout)
        password_layout.addSpacing(10)
        password_layout.addWidget(confirm_label)
        password_layout.addLayout(confirm_field_layout)
        password_layout.addWidget(self.match_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedSize(130, 42)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        
        self.create_button = QPushButton("Create Password")
        self.create_button.setObjectName("create_button")
        self.create_button.setFixedSize(160, 42)
        self.create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_button.setEnabled(False)
        self.create_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        
        # Add all components to container layout
        container_layout.addLayout(header_layout)
        container_layout.addWidget(warning_frame)
        container_layout.addLayout(password_layout)
        container_layout.addWidget(policy_frame)
        container_layout.addStretch()
        container_layout.addLayout(button_layout)
        
        # Add container to main layout
        main_layout.addWidget(self.container)
        
        # Apply stylesheets
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            
            #title_label {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                background: transparent;
            }
            
            #subtitle_label {
                font-size: 12px;
                color: #b0b0b0;
                background: transparent;
            }
            
            #warning_frame {
                background-color: #4d3030;
                border-radius: 6px;
                padding: 10px;
                color: #f0c0c0;
            }
            
            #password_field {
                background-color: #3d3d3d;
                border: 1px solid #505050;
                border-radius: 4px;
                color: #f0f0f0;
                padding: 5px 10px;
                font-size: 14px;
            }
            
            #password_field:focus {
                border: 1px solid #4C86D0;
            }
            
            #toggle_button {
                background-color: #3d3d3d;
                border: 1px solid #505050;
                border-radius: 4px;
                color: #b0b0b0;
                font-size: 16px;
                padding: 0;
            }
            
            #toggle_button:hover {
                background-color: #4d4d4d;
                color: #f0f0f0;
            }
            
            #toggle_button:pressed {
                background-color: #2d2d2d;
                color: #4C86D0;
            }
            
            #strength_bar {
                border-radius: 4px;
                background-color: #3d3d3d;
            }
            
            #strength_bar::chunk {
                border-radius: 4px;
            }
            
            #strength_label {
                color: #b0b0b0;
                font-size: 12px;
                background: transparent;
            }
            
            #policy_frame {
                background-color: #353540;
                border-radius: 6px;
                padding: 10px;
            }
            
            #policy_title {
                font-weight: bold;
                color: #c0c0c0;
                background: transparent;
            }
            
            #policy_item {
                color: #b0b0b0;
                padding: 3px 0;
                background: transparent;
            }
            
            #match_label {
                color: #4CAF50;
                font-size: 12px;
                padding: 5px 0;
                background: transparent;
            }
            
            QLabel {
                background: transparent;
                color: #f0f0f0;
            }
            
            #cancel_button {
                background-color: #3d3d3d;
                color: #f0f0f0;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            #cancel_button:hover {
                background-color: #4d4d4d;
            }
            
            #cancel_button:pressed {
                background-color: #2d2d2d;
            }
            
            #create_button {
                background-color: #4C86D0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            
            #create_button:hover {
                background-color: #5A9BE7;
            }
            
            #create_button:pressed {
                background-color: #3C76C0;
            }
            
            #create_button:disabled {
                background-color: #656565;
                color: #a0a0a0;
            }
        """)

    def check_password_strength(self):
        """Check password strength and update UI indicators"""
        password = self.password_field.text()
        strength = 0
        color = "#FF6B6B"  # Red - Very Weak
        
        # Check length
        if len(password) >= 8:
            self.length_check.setText("✅ At least 8 characters")
            strength += 25
        else:
            self.length_check.setText("❌ At least 8 characters")
        
        # Check uppercase
        if re.search(r'[A-Z]', password):
            self.uppercase_check.setText("✅ At least 1 uppercase letter")
            strength += 25
        else:
            self.uppercase_check.setText("❌ At least 1 uppercase letter")
        
        # Check digits
        if re.search(r'\d', password):
            self.digit_check.setText("✅ At least 1 number")
            strength += 25
        else:
            self.digit_check.setText("❌ At least 1 number")
        
        # Check special chars
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.special_check.setText("✅ At least 1 special character")
            strength += 25
        else:
            self.special_check.setText("❌ At least 1 special character")
        
        # Update strength bar color and text
        if strength <= 25:
            color = "#FF6B6B"  # Red - Very Weak
            strength_text = "Too Weak"
        elif strength <= 50:
            color = "#FFB947"  # Orange - Weak
            strength_text = "Weak"
        elif strength <= 75:
            color = "#FCD34D"  # Yellow - Medium
            strength_text = "Medium"
        else:
            color = "#4CAF50"  # Green - Strong
            strength_text = "Strong"
        
        self.strength_bar.setStyleSheet(f"#strength_bar::chunk {{ background-color: {color}; }}")
        self.strength_bar.setValue(strength)
        self.strength_label.setText(f"Password Strength: {strength_text}")
        
        # Update match status after checking strength
        self.check_passwords_match()
    
    def check_passwords_match(self):
        """Check if passwords match and update UI"""
        password = self.password_field.text()
        confirm = self.confirm_field.text()
        
        if not confirm:
            self.match_label.setText("")
            self.create_button.setEnabled(False)
            return
        
        if password == confirm:
            self.match_label.setText("✅ Passwords match")
            self.match_label.setStyleSheet("#match_label { color: #4CAF50; background: transparent; }")
            
            # Only enable button if password meets requirements
            if (len(password) >= 8 and 
                re.search(r'[A-Z]', password) and 
                re.search(r'\d', password) and 
                re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
                self.create_button.setEnabled(True)
            else:
                self.create_button.setEnabled(False)
        else:
            self.match_label.setText("❌ Passwords do not match")
            self.match_label.setStyleSheet("#match_label { color: #FF6B6B; background: transparent; }")
            self.create_button.setEnabled(False)
    
    def toggle_password_visibility(self, field):
        """Toggle password visibility for a specific field"""
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            if field == self.password_field:
                self.toggle_password_btn.setIcon(QIcon("Icon/eye.png"))
            else:
                self.toggle_confirm_btn.setIcon(QIcon("Icon/eye.png"))
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            if field == self.password_field:
                self.toggle_password_btn.setIcon(QIcon("Icon/eye-off.png"))
            else:
                self.toggle_confirm_btn.setIcon(QIcon("Icon/eye-off.png"))

    
    def get_password(self):
        """Return the entered password"""
        return self.password_field.text()
        
    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set up the layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create the loading label
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
        """)
        
        self.layout.addWidget(self.loading_label)
        self.setLayout(self.layout)
        
        # Hide by default
        self.hide()
    
    def setText(self, text):
        self.loading_label.setText(text)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))
        super().paintEvent(event)


class NetworkImageLoader(QWidget):
    def __init__(self, url, size=40):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.size = size
        self.label = QLabel()
        self.label.setFixedSize(size, size)
        self.label.setScaledContents(True)
        self.label.setStyleSheet("border-radius: {}px; background-color: #333;".format(size//2))
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Keep a reference to the reply to prevent it from being garbage collected
        self.reply = None
        self.load_image(url)
    
    def load_image(self, url):
        request = QNetworkRequest(QUrl(url))
        self.reply = self.network_manager.get(request)
        self.reply.finished.connect(self.on_image_loaded)
    
    def on_image_loaded(self):
        if self.reply and self.reply.error() == QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(self.reply.readAll())
            
            # Apply the pixmap to the label
            self.label.setPixmap(pixmap)
            
        # Clean up the reply
        if self.reply:
            self.reply.deleteLater()
            self.reply = None


class FileTableWidget(QTableWidget):
    file_download_requested = pyqtSignal(int)  # row index
    file_share_requested = pyqtSignal(int)
    file_rename_requested = pyqtSignal(int)
    file_delete_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Type", "Size", "Last Modified"])
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        
        # Configure column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name column stretches
        self.setColumnWidth(1, 120)  # Type column width
        self.setColumnWidth(2, 100)  # Size column width
        self.setColumnWidth(3, 150)  # Last Modified column width
        
        # Set custom fonts
        header_font = QFont("Segoe UI", 10, QFont.Weight.DemiBold)
        self.horizontalHeader().setFont(header_font)
        
        # Custom row heights for better spacing
        self.verticalHeader().setDefaultSectionSize(50)
        
        # Adding selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Improved mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Applying the consistent color scheme to match with other components
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: none;
                gridline-color: transparent;
                outline: none;
                border-radius: 8px;
                padding: 5px;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #3d3d3d;
                margin: 3px;
                border-radius: 4px;
            }
            
            QTableWidget::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #3C76C0, stop:1 #4C86D0);
                color: #ffffff;
                border-radius: 4px;
            }
            
            QTableWidget::item:hover:!selected {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
            
            QHeaderView::section {
                background-color: #252525;
                color: #b0b0b0;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #3d3d3d;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 10px;
            }
            
            QHeaderView::section:hover {
                background-color: #353535;
                color: #d0d0d0;
            }
            
            QHeaderView::section:pressed {
                background-color: #404040;
            }
            
            QTableWidget QTableCornerButton::section {
                background-color: #252525;
                border: none;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #252525;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #4d4d4d;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #5A9BE7;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: #252525;
                height: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:horizontal {
                background-color: #4d4d4d;
                border-radius: 4px;
                min-width: 30px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: #5A9BE7;
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add hover effect
        self.cellEntered.connect(self.on_cell_hover)
        
        # Allow users to resize columns manually
        self.horizontalHeader().setSectionsMovable(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Except Name column
        
    def on_cell_hover(self, row, column):
        # Could be used for custom hover effects if needed
        pass
        
    def set_column_widths(self, widths):
        """
        Set custom column widths
        
        Args:
            widths: List of column widths [name_col, type_col, size_col, modified_col]
                   Use -1 for stretch mode on a column
        """
        if not widths or len(widths) != 4:
            return
            
        # Reset all columns to Interactive mode first
        for i in range(self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            
        # Set specified widths
        for i, width in enumerate(widths):
            if width == -1:
                # Use stretch mode for this column
                self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                # Set fixed width
                self.setColumnWidth(i, width)

    def populate_table(self, files):
        self.setRowCount(0)
        
        # Add smooth animation when populating
        self.setUpdatesEnabled(False)
        
        for row_idx, file in enumerate(files):
            name = file.get('name', '')
            mime = file.get('mimeType', '')
            
            # Format size with improved readability
            size_bytes = file.get('size', '')
            if size_bytes and size_bytes.isdigit():
                size_int = int(size_bytes)
                if size_int < 1024:
                    size = f"{size_int} bytes"
                elif size_int < 1024 * 1024:
                    size = f"{size_int / 1024:.1f} KB"
                elif size_int < 1024 * 1024 * 1024:
                    size = f"{size_int / (1024 * 1024):.1f} MB"
                else:
                    size = f"{size_int / (1024 * 1024 * 1024):.1f} GB"
            else:
                size = size_bytes + " bytes" if size_bytes else "—"
            
            # Format modified time with more readable format
            modified = file.get('modifiedTime', '')
            if modified:
                try:
                    # Parse ISO format datetime
                    from datetime import datetime, timezone
                    mod_time = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    
                    # Calculate relative time (today, yesterday, etc)
                    now = datetime.now(timezone.utc)
                    diff = now - mod_time
                    
                    if diff.days == 0:
                        # Today - show time only
                        modified = f"Today, {mod_time.strftime('%H:%M')}"
                    elif diff.days == 1:
                        # Yesterday
                        modified = f"Yesterday, {mod_time.strftime('%H:%M')}"
                    elif diff.days < 7:
                        # This week
                        modified = mod_time.strftime("%A, %H:%M")
                    else:
                        # Older
                        modified = mod_time.strftime("%b %d, %Y")
                except:
                    pass  # Keep the original format if parsing fails
            
            # Insert a new row
            self.insertRow(row_idx)
            
            # Set custom row height
            self.setRowHeight(row_idx, 45)
            
            # Name with prettier icon
            name_item = QTableWidgetItem(name)
            name_item.setToolTip(name)  # Add tooltip for long names
            
            # Use more attractive icons based on MIME type
            icon_size = QSize(24, 24)
            
            # Updated color scheme for icons to match our theme
            if "folder" in mime.lower():
                name_item.setIcon(self.get_styled_icon("folder", "#4C86D0"))
            elif "document" in mime.lower() or "doc" in mime.lower():
                name_item.setIcon(self.get_styled_icon("x-office-document", "#5A9BE7"))
            elif "spreadsheet" in mime.lower() or "excel" in mime.lower() or "sheet" in mime.lower():
                name_item.setIcon(self.get_styled_icon("x-office-spreadsheet", "#3C76C0"))
            elif "presentation" in mime.lower() or "powerpoint" in mime.lower() or "slide" in mime.lower():
                name_item.setIcon(self.get_styled_icon("x-office-presentation", "#6BABF7"))
            elif "image" in mime.lower() or "photo" in mime.lower():
                name_item.setIcon(self.get_styled_icon("image-x-generic", "#5A9BE7"))
            elif "pdf" in mime.lower():
                name_item.setIcon(self.get_styled_icon("application-pdf", "#4C86D0"))
            elif "zip" in mime.lower() or "archive" in mime.lower() or "tar" in mime.lower():
                name_item.setIcon(self.get_styled_icon("application-x-archive", "#3C76C0"))
            elif "text" in mime.lower() or "txt" in mime.lower():
                name_item.setIcon(self.get_styled_icon("text-x-generic", "#5A9BE7"))
            elif "audio" in mime.lower() or "music" in mime.lower() or "sound" in mime.lower():
                name_item.setIcon(self.get_styled_icon("audio-x-generic", "#6BABF7"))
            elif "video" in mime.lower():
                name_item.setIcon(self.get_styled_icon("video-x-generic", "#4C86D0"))
            else:
                name_item.setIcon(self.get_styled_icon("application-x-executable", "#e0e0e0"))
            
            # Create readable type name from MIME
            type_display = self.get_friendly_type_name(mime)
            type_item = QTableWidgetItem(type_display)
            type_item.setToolTip(mime)  # Show full MIME type on hover
            
            # Size item with right alignment
            size_item = QTableWidgetItem(size)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Set items in table
            self.setItem(row_idx, 0, name_item)
            self.setItem(row_idx, 1, type_item)
            self.setItem(row_idx, 2, size_item)
            self.setItem(row_idx, 3, QTableWidgetItem(modified))
            
        # Re-enable updates with all rows added at once
        self.setUpdatesEnabled(True)
    
    def get_styled_icon(self, icon_name, color_hex="#ffffff"):
        """Get a colorized icon from theme"""
        icon = QIcon.fromTheme(icon_name)
        
        # This method would ideally colorize the icon
        # For a full implementation, you would need to add code to
        # apply a color overlay to the icon using QPainter
        
        return icon
    
    def get_friendly_type_name(self, mime):
        """Convert MIME type to user-friendly name"""
        if "folder" in mime.lower():
            return "Folder"
        elif "document" in mime.lower() or "doc" in mime.lower():
            return "Document"
        elif "spreadsheet" in mime.lower() or "excel" in mime.lower() or "sheet" in mime.lower():
            return "Spreadsheet"
        elif "presentation" in mime.lower() or "powerpoint" in mime.lower() or "slide" in mime.lower():
            return "Presentation"
        elif "image" in mime.lower() or "photo" in mime.lower():
            return "Image"
        elif "pdf" in mime.lower():
            return "PDF"
        elif "zip" in mime.lower() or "archive" in mime.lower() or "tar" in mime.lower():
            return "Archive"
        elif "text" in mime.lower() or "txt" in mime.lower():
            return "Text"
        elif "audio" in mime.lower() or "music" in mime.lower() or "sound" in mime.lower():
            return "Audio"
        elif "video" in mime.lower():
            return "Video"
        elif "/" in mime:
            # Try to extract second part of MIME type (e.g., "pdf" from "application/pdf")
            return mime.split("/")[1].capitalize()
        else:
            return "File"

    def show_context_menu(self, position):
        if self.currentRow() < 0:
            return
        
        # Create stylish context menu
        context_menu = StylishContextMenu(self)
        
        # Create actions with icons
        actions = {
            "download": {"text": "Download", "icon": "download_icon.png", "emoji": "⬇️"},
            "share": {"text": "Share", "icon": "share_icon.png", "emoji": "📤"},
            "rename": {"text": "Rename", "icon": "rename_icon.png", "emoji": "✏️"},
            "delete": {"text": "Delete", "icon": "delete_icon.png", "emoji": "🗑️"}
        }
        
        menu_actions = {}
        for key, data in actions.items():
            action = context_menu.addStylishAction(data["icon"], data["emoji"], data["text"])
            menu_actions[key] = action
            
            # Add separator before delete
            if key == "rename":
                context_menu.addSeparator()
        
        # Calculate position adjustments to look nicer
        adjusted_position = self.mapToGlobal(position)
        
        # Get selected row
        selected_row = self.currentRow()
        
        # Execute menu and handle result
        chosen_action = context_menu.exec(adjusted_position)
        
        # Handle actions
        if chosen_action == menu_actions["download"]:
            self.file_download_requested.emit(selected_row)
        elif chosen_action == menu_actions["share"]:
            self.file_share_requested.emit(selected_row)
        elif chosen_action == menu_actions["rename"]:
            self.file_rename_requested.emit(selected_row)
        elif chosen_action == menu_actions["delete"]:
            self.file_delete_requested.emit(selected_row)


class StylishContextMenu(QMenu):
    """A stylish context menu with rounded corners, animations and hover effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d3d3d;
                margin: 5px 15px;
            }
        """)
        
        # Animation settings
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def addStylishAction(self, icon_path, emoji_fallback, text):
        """Add a stylish action to the menu"""
        action = self._createStylishMenuAction(icon_path, emoji_fallback, text)
        self.addAction(action)
        return action
    
    def _createStylishMenuAction(self, icon_path, emoji_fallback, text):
        """Internal method to create a stylish menu action"""
        action = QWidgetAction(self)
        
        # Create custom widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(0)
        
        # Action label with icon and text
        label = QLabel()
        label.setFont(QFont("Arial", 10))
        
        # Try to load icon, use emoji fallback
        if QFile(icon_path).exists():
            pixmap = QPixmap(icon_path).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
            label.setText(f"   {text}")
            label.setPixmap(pixmap)
        else:
            label.setText(f" {emoji_fallback}  {text}")
        
        label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                padding: 4px 8px;
                border-radius: 4px;
                background: transparent;
            }
        """)
        
        layout.addWidget(label)
        action.setDefaultWidget(container)
        
        # Store references to the widgets for use in the event filter
        action.container = container
        action.label = label
        
        # Install event filter to handle hover events
        class EventFilter(QObject):
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.Enter:
                    label.setStyleSheet("""
                        QLabel {
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            background: rgba(76, 134, 208, 0.7);
                        }
                    """)
                    return True
                elif event.type() == QEvent.Type.Leave:
                    label.setStyleSheet("""
                        QLabel {
                            color: #e0e0e0;
                            padding: 4px 8px;
                            border-radius: 4px;
                            background: transparent;
                        }
                    """)
                    return True
                return False
        
        event_filter = EventFilter()
        container.installEventFilter(event_filter)
        # Keep a reference to the event filter to prevent garbage collection
        action.event_filter = event_filter
        
        return action
    
    def showEvent(self, event):
        super().showEvent(event)
        self.animation.start()
    
    def paintEvent(self, event):
        # Custom painting for rounded corners
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw rounded rectangle for the background
        path = QPainterPath()
        rect = self.rect()
        # Convert QRect to coordinates for addRoundedRect
        path.addRoundedRect(
            float(rect.x()), 
            float(rect.y()), 
            float(rect.width()), 
            float(rect.height()), 
            8.0, 8.0
        )
        
        # Draw menu background
        painter.setBrush(QColor(45, 45, 45))  # #2d2d2d
        painter.drawPath(path)


class SidebarButton(QPushButton):
    def __init__(self, text, icon_name=None):
        super().__init__(text)
        if icon_name:
            self.setIcon(QIcon.fromTheme(icon_name))
        
        # Enhanced font and sizing
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(45)
        self.setIconSize(QSize(24, 24))
        
        # Set text and icon alignment
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        # No need for property animation as we're using stylesheets for visual effects
        
        # Modern styling with gradient and animations
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #f0f0f0;
                padding: 8px 16px;
                text-align: left;
                font-weight: medium;
                margin: 2px 5px;
                spacing: 12px;
            }
            
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                stop:0 #3d3d3d, stop:1 #464646);
                color: #ffffff;
                border-left: 3px solid #6a7bff;
            }
            
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                stop:0 #464646, stop:1 #555555);
                color: #ffffff;
                border-left: 3px solid #4a5bff;
            }
            
            QPushButton:checked {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                stop:0 #353535, stop:1 #454545);
                border-left: 3px solid #6a7bff;
                color: #ffffff;
            }
            
            QPushButton::icon {
                margin-right: 10px;
            }
        """)
        
    def enterEvent(self, event):
        # Add subtle animation when hovering
        self.setGraphicsEffect(QGraphicsDropShadowEffect(
            blurRadius=10, 
            color=QColor(0, 0, 0, 50),
            offset=QPointF(0, 0)
        ))
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # Remove effects when mouse leaves
        self.setGraphicsEffect(None)
        super().leaveEvent(event)