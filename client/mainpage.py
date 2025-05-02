# drivebuddy/ui_main.py

import os, threading, shutil
from googleapiclient.discovery import build
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QProgressBar, QLabel, QFrame, QSizePolicy, QSpacerItem,
    QLineEdit, QApplication
)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from drive_api import *
from auth import get_user_info
from ui_helper import *

class SignalEmitter(QObject):
    refresh_done = pyqtSignal(list)
    download_done = pyqtSignal(str)
    upload_done = pyqtSignal(dict)
    share_done = pyqtSignal(str)
    file_deleted = pyqtSignal(str)
    file_renamed = pyqtSignal(str)
    loading_done = pyqtSignal()
    logged_out = pyqtSignal()
    error = pyqtSignal(str)
    search_failed = pyqtSignal(str)
    upload_failed = pyqtSignal(str)
    download_failed = pyqtSignal(str)
    share_failed = pyqtSignal(str)
    delete_failed = pyqtSignal(str)
    renaming_failed = pyqtSignal(str)

class MainPage(QWidget):
    def __init__(self, creds=None, umk=None):
        super().__init__()
        self.signals = SignalEmitter()
        self.creds = creds
        self.user_master_key = umk
        self.user_details = get_user_info(creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.files = []  # Initialize files list
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)
        
        # Set window title and size
        self.setWindowTitle("SafeDrive")
        self.resize(1200, 800)
        
        # Set the dark theme
        self.set_dark_theme()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add header
        self.init_header()
        main_layout.addWidget(self.header_frame)
        
        # Content area (sidebar + table)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Add sidebar
        self.init_sidebar()
        content_layout.addWidget(self.sidebar_frame)
        
        # Add file table
        self.file_table = FileTableWidget()
        content_layout.addWidget(self.file_table)
        self.file_table.file_download_requested.connect(self.download_selected_file)
        self.file_table.file_share_requested.connect(self.share_selected_file)
        self.file_table.file_rename_requested.connect(self.rename_selected_file)
        self.file_table.file_delete_requested.connect(self.delete_selected_file)
        
        # Add content to main layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Add footer
        self.init_footer()
        main_layout.addWidget(self.footer_frame)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Setup signal connections
        self.setup_signals()
        
        # Initialize status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #919191;")
        main_layout.addWidget(self.status_label)
        
        # Initialize with user's files
        self.show_owned_by_me()
    
    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 55))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(66, 133, 244))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(dark_palette)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #5d5d5d;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #2d2d2d;
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #5d5d5d;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
        """)
    
    def init_header(self):
        # Create header frame
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(64)
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #272727;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # App logo and name
        logo_label = QLabel("SafeDrive")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #4285F4;") # Google blue
        
        header_layout.addWidget(logo_label)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search files...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                border: none;
                border-radius: 4px;
                color: #f0f0f0;
                padding: 8px;
                margin: 0 20px;
            }
            QLineEdit:focus {
                background-color: #444;
                border: 1px solid #5d5d5d;
            }
        """)
        self.search_edit.returnPressed.connect(self.search_files)
        header_layout.addWidget(self.search_edit)
        
        # Add spacer
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        
        # User greeting and info
        if self.user_details:
            # Greeting with user's name
            greeting_text = "Welcome, " + self.user_details["name"].split()[0]
            greeting_label = QLabel(greeting_text)
            greeting_label.setFont(QFont("Segoe UI", 12))
            header_layout.addWidget(greeting_label)
            
            # Profile picture
            if self.user_details.get("profile_pic"):
                profile_pic = NetworkImageLoader(self.user_details["profile_pic"], 40)
                header_layout.addWidget(profile_pic)
        
        # Set layout
        self.header_frame.setLayout(header_layout)
    
    def init_sidebar(self):
        # Create sidebar frame
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(220)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #272727;
                border-right: 1px solid #3d3d3d;
            }
        """)
        
        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(8)
        
        # Create buttons
        self.my_files_btn = SidebarButton("My Files", "folder")
        self.shared_btn = SidebarButton("Shared with me", "folder-publicshare")
        self.refresh_btn = SidebarButton("Refresh", "view-refresh")
        self.upload_btn = SidebarButton("Upload File", "document-new")
        
        # Add buttons to layout
        sidebar_layout.addWidget(self.my_files_btn)
        sidebar_layout.addWidget(self.shared_btn)
        sidebar_layout.addWidget(self.upload_btn)
        sidebar_layout.addWidget(self.refresh_btn)
        
        # Add spacer to push content to the top
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Connect button signals
        self.my_files_btn.clicked.connect(self.show_owned_by_me)
        self.shared_btn.clicked.connect(self.show_shared_with_me)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        self.upload_btn.clicked.connect(self.upload_file)

        # Set layout
        self.sidebar_frame.setLayout(sidebar_layout)

    def init_footer(self):
        # Create footer frame
        self.footer_frame = QFrame()
        self.footer_frame.setFixedHeight(50)
        self.footer_frame.setStyleSheet("""
            QFrame {
                background-color: #272727;
                border-top: 1px solid #3d3d3d;
            }
        """)
        
        # Footer layout
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 0, 20, 0)
        
        # Storage usage section
        storage_layout = QHBoxLayout()
        storage_layout.setSpacing(10)
        
        # Storage progress bar
        storage_info = self.get_storage_info() 
        total_storage = storage_info["total"]
        used_storage = storage_info["used"]
        used_percent = int((used_storage / total_storage) * 100)

        # Storage progress bar
        storage_progress = QProgressBar()
        storage_progress.setRange(0, 100)
        storage_progress.setValue(used_percent)  # Set actual used percent
        storage_progress.setFixedWidth(150)
        storage_progress.setFixedHeight(10)
        storage_progress.setTextVisible(False)
        storage_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #3d3d3d;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4285F4;
                border-radius: 5px;
            }
        """)

        # Format text like "5.2 GB of 15 GB used"
        used_gb = used_storage / (1024 ** 3)
        total_gb = total_storage / (1024 ** 3)
        storage_text = QLabel(f"{used_gb:.2f} GB of {total_gb:.2f} GB used")
        storage_text.setFont(QFont("Segoe UI", 9))

        # Layout for storage
        storage_layout = QHBoxLayout()
        storage_layout.addWidget(storage_progress)
        storage_layout.addWidget(storage_text)

        # Add storage section to footer
        footer_layout.addLayout(storage_layout)
        
        # Add spacer
        footer_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Segoe UI", 10))
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f0f0f0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        footer_layout.addWidget(logout_btn)
        
        # Set layout
        self.footer_frame.setLayout(footer_layout)

    def refresh_file_list(self):
        self.show_loading("Refreshing files...")
        if hasattr(self, 'current_view') and self.current_view == 'shared':
            self.show_shared_with_me()
        else:
            self.show_owned_by_me()

    def search_files(self):
        search_text = self.search_edit.text().lower()
        if not search_text:
            self.refresh_file_list()
            return

        self.status_label.setText(f"Searching for '{search_text}'...")
        self.show_loading("Searching...")

        def task():
            try:
                matching_files = search_drive_files(self.drive_service, search_text)
                self.files = matching_files
                self.signals.refresh_done.emit(matching_files)
            except Exception as e:
                self.signals.search_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()

        threading.Thread(target=task).start()

    def update_file_table(self, files):
        self.files = files
        self.file_table.populate_table(files)
        self.status_label.setText(f"Found {len(files)} files")

    def show_loading(self, text="Loading..."):
        self.loading_overlay.setText(text)
        self.loading_overlay.resize(self.width(), self.height())
        self.loading_overlay.show()

    def hide_loading(self):
        self.loading_overlay.hide()

    def rename_selected_file(self, row_index=None):
        if row_index is None:
            selected = self.file_table.currentRow()
        else:
            selected = row_index
            
        if selected == -1:
            dialog = CustomErrorDialog("Rename", "Please select a file to rename.", self.parent()) 
            dialog.exec()
            return

        file = self.files[selected]
        file_id = file.get('id')
        current_name = file.get('name')

        if current_name.lower().endswith('.enc'):
            dialog = CustomErrorDialog("Rename Not Allowed", "Cannot rename encrypted (.enc) files.", self.parent()) 
            dialog.exec()
            return
        
        dialog = CustomRenameDialog("Rename File", "Enter new name:", current_name)
        if dialog.exec():
            new_name = dialog.get_new_name()
        else:
            return

        new_name = new_name.strip()
        if new_name == "":
            dialog = CustomErrorDialog("Invalid Name", "File name cannot be empty.", self.parent()) 
            dialog.exec()
            return

        self.show_loading(f"Renaming '{current_name}' to '{new_name}'...")

        def task():
            try:
                rename_drive_file(self.drive_service, file_id, new_name)
                file['name'] = new_name
                self.signals.file_renamed.emit(new_name)
            except Exception as e:
                self.signals.renaming_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()
                # Refresh the table to show the updated file name
                QApplication.processEvents()
                self.file_table.populate_table(self.files)

        threading.Thread(target=task).start()

    def delete_selected_file(self, row_index=None):
        if row_index is None:
            selected = self.file_table.currentRow()
        else:
            selected = row_index
            
        if selected == -1:
            dialog = CustomErrorDialog("Delete", "Please select a file to delete.", self.parent())
            dialog.exec()
            return

        file = self.files[selected]
        file_name = file.get('name')

        msg_box = CustomMessageBox("Confirm Delete", 
            f"Are you sure you want to delete '{file_name}'?", parent=self)
        result = msg_box.exec()
        
        if result != QDialog.DialogCode.Accepted:
            return

        file_id = file.get('id')
        is_shared = file.get('shared', False)

        self.show_loading(f"Deleting '{file_name}'...")

        def task():
            try:
                delete_drive_file(self.drive_service, file_id)
                self.signals.file_deleted.emit(file_name)
                # Update the files list
                self.files.pop(selected)
            except Exception as e:
                self.signals.delete_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()
                # Refresh the table to remove the deleted file
                QApplication.processEvents()
                self.file_table.populate_table(self.files)

        threading.Thread(target=task).start()

    def upload_file(self):
        """Upload a file to Google Drive."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select File to Upload")
        if not file_path:
            return
        
        decryptor = SecretKeyDecryptor(self)
        master_key = decryptor.decrypt(self.user_master_key)
        if not master_key:
            return  # Decryption failed or cancelled
    
        self.show_loading(f"Uploading '{os.path.basename(file_path)}'...")
        
        def task():
            try:
                result = upload_file(self.drive_service, file_path, master_key)
                self.signals.upload_done.emit(result)
            except Exception as e:
                self.signals.upload_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()
                
        threading.Thread(target=task).start()


    def show_owned_by_me(self):
        """Display files owned by the current user."""
        self.show_loading("Loading your files...")
        
        def task():
            try:
                files = list_owned_by_me(self.drive_service)
                self.files = files  # Update files list
                self.signals.refresh_done.emit(files)
            except Exception as e:
                self.signals.error.emit(f"Failed to fetch file list: {str(e)}")
            finally:
                self.signals.loading_done.emit()
                
        threading.Thread(target=task).start()


    def show_shared_with_me(self):
        """Display files shared with the current user."""
        self.show_loading("Loading shared files...")
        
        def task():
            try:
                files = list_shared_with_me(self.drive_service)
                self.files = files  # Update files list
                self.signals.refresh_done.emit(files)
            except Exception as e:
                self.signals.error.emit(f"Failed to fetch shared files: {str(e)}")
            finally:
                self.signals.loading_done.emit()
                
        threading.Thread(target=task).start()


    def download_selected_file(self):
        """Download the selected file from Google Drive."""
        selected = self.file_table.currentRow()
        if selected == -1:
            dialog = CustomErrorDialog("Download", "Please select a file to download.", self.parent())
            dialog.exec()
            return

        file = self.files[selected]
        file_id = file.get('id')
        file_name = file.get('name')
        is_shared = file.get('shared')

        folder = QFileDialog.getExistingDirectory(self, "Select Download Location")
        if not folder:
            return

        save_path = os.path.join(folder, file_name)

        # Decrypt master key in main thread
        if file_name.endswith(".enc") and not is_shared:
            decryptor = SecretKeyDecryptor(self)
            master_key = decryptor.decrypt(self.user_master_key)
            if not master_key:
                return  # User cancelled
        else:
            master_key = None

        def task():
            try:
                download_file_core(self.drive_service, file_id, is_shared, save_path, master_key)
                self.signals.download_done.emit(save_path)
            except Exception as e:
                self.signals.download_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()

        threading.Thread(target=task).start()


    def share_selected_file(self):
        """Share the selected file with another user."""
        selected = self.file_table.currentRow()
        if selected == -1:
            dialog = CustomErrorDialog("Share", "Please select a file to share.", self.parent())
            dialog.exec()
            return

        dialog = CustomEmailDialog("Share File", "Enter email to share with:", self)
        if dialog.exec():
            email = dialog.get_email()
        else:
            return

        file = self.files[selected]
        file_id = file.get('id')
        file_name = file.get('name')

        # Decrypt master key in the main thread
        decryptor = SecretKeyDecryptor(self)
        master_key = decryptor.decrypt(self.user_master_key)
        if not master_key:
            return  # User cancelled

        self.show_loading(f"Sharing '{file_name}' with {email}...")

        def task():
            try:
                share_file(self.drive_service, file_id, file_name, email, master_key)
                self.signals.share_done.emit(email)
            except Exception as e:
                self.signals.share_failed.emit(str(e))
            finally:
                self.signals.loading_done.emit()

        threading.Thread(target=task).start()



    def setup_signals(self):
        """Connect signals to their respective slots."""
        self.signals.refresh_done.connect(self.update_file_table)

        self.signals.download_done.connect(
            lambda msg: CustomSuccessDialog("Download", f"Downloaded to: {msg}", self).exec()
        )
        self.signals.upload_done.connect(
            lambda data: CustomSuccessDialog("Upload", f"{data['name']} uploaded successfully!", self).exec()
        )
        self.signals.share_done.connect(
            lambda msg: CustomSuccessDialog("Share", f"File shared with: {msg}", self).exec()
        )
        self.signals.file_deleted.connect(
            lambda msg: CustomSuccessDialog("Delete", f"{msg} Deleted Successfully!", self).exec()
        )
        self.signals.file_renamed.connect(
            lambda msg: CustomSuccessDialog("Renmae",f"File renamed to: {msg}", self).exec()
        )

        self.signals.loading_done.connect(self.hide_loading)

        self.signals.error.connect(
            lambda msg: CustomErrorDialog(msg, self).exec()
        )

        self.signals.logged_out.connect(self.handle_logout)


    def handle_logout(self):
        if self.parent():
            self.parent().show_home_page()
            
    def logout(self):
        """Log out the current user by clearing cache and tokens."""
        msg_box = CustomMessageBox("Logout",
            "Are you sure you want to logout?", parent=self)
        result = msg_box.exec()

        if result != QDialog.DialogCode.Accepted: 
            return
            
        self.show_loading("Logging out...")
        
        def task():
            try:
                # 1. Delete cache folder if it exists
                cache_path = os.path.join(os.getcwd(), 'cache')
                if os.path.exists(cache_path) and os.path.isdir(cache_path):
                    shutil.rmtree(cache_path)
                    
                # 2. Delete all files ending with 'token.json' in current directory
                for filename in os.listdir(os.getcwd()):
                    if filename.endswith('token.json'):
                        file_path = os.path.join(os.getcwd(), filename)
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            dialog = CustomErrorDialog("Error", f"Failed to delete {file_path}: {e}", self.parent())
                            dialog.exec_()
                            
                # 3. Signal to return to login screen (don't directly manipulate UI)
                self.signals.logged_out.emit()
            except Exception as e:
                self.signals.error.emit(f"Logout failed: {str(e)}")
            finally:
                self.signals.loading_done.emit()
                # Don't call UI methods directly from thread
                # self.parent().show_home_page()  # REMOVE THIS
                
        threading.Thread(target=task).start()
        
        # Connect the logged_out signal to show_home_page method
        self.signals.logged_out.connect(lambda: self.parent().show_home_page())



    def get_storage_info(self):
        about = self.drive_service.about().get(fields="storageQuota").execute()
        storage_quota = about.get('storageQuota')

        limit = int(storage_quota.get('limit'))
        usage = int(storage_quota.get('usage'))
        usage_in_drive = int(storage_quota.get('usageInDrive'))
        usage_in_trash = int(storage_quota.get('usageInDriveTrash'))

        return {
            "total": limit,
            "used": usage,
            "used_in_drive": usage_in_drive,
            "used_in_trash": usage_in_trash,
        }