import sys, os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QFont
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from auth import SCOPE, DRIVE_TOKEN
from mainpage import *
from homepage import *
from auth import get_user_info
from key_manager import *

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SafeDrive')
        self.setFixedSize(1250, 800)
        self.center_window()
        
        if os.path.exists(DRIVE_TOKEN):
            creds = Credentials.from_authorized_user_file(DRIVE_TOKEN, SCOPE)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            # Create and show the main page
            user_details = get_user_info(creds)
            if creds and creds.valid:
                email = user_details["email"]
                self.key_manager = KeyManager(email, parent=self)
                if not self.key_manager.enc_umk:
                    msg_box = CustomMessageBox("Key Not Found", "No valid key was found or registration was cancelled.\nWould you like to retry?", parent=self)
                    result = msg_box.exec()

                    if result == QDialog.DialogCode.Accepted:  # User clicked Yes or Retry
                        self.key_manager = KeyManager(email, parent=self)
                        if not self.key_manager.enc_umk:
                            error_box = CustomErrorDialog("Aborted", "Key still not available. Exiting.", parent=self)
                            error_box.exec()
                            sys.exit()
                        else:
                            sys.exit()

                #self.main_page = MainPage(creds, self.key_manager.enc_umk)
                self.show_main_page(creds, self.key_manager.enc_umk)
            else:
                dialog = CustomErrorDialog("Invalid or missing credentials!", self)
                dialog.exec()
        else:
            # Show home page where user can login via Google
            self.home_page = HomePage()
            self.home_page.setParent(self) # Set App as the parent widget
            self.home_page.show()
    
    def center_window(self):
        """Center the window on the screen"""
        # Get the screen geometry
        screen = QApplication.primaryScreen().geometry()
        # Calculate center position
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # Move window to center
        self.move(x, y)
    
    def show_home_page(self):
        """Switch back to the home page."""
        self.home_page = HomePage()
        self.home_page.setParent(self)
        self.home_page.show()

        if hasattr(self, 'main_page'):
            self.main_page.hide()
    
    def show_main_page(self, creds, umk):
        self.main_page = MainPage(creds, umk)
        self.main_page.setParent(self)
        self.main_page.show()
        
        if hasattr(self, 'home_page'):
            self.home_page.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set global font and spacing
    font = QFont('Segoe UI', 10)
    app.setFont(font)
    
    window = App()
    window.show()
    sys.exit(app.exec())