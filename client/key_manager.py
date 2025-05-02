# key_manager.py

import sys
import os
import requests
import base64
import json
from PyQt6.QtWidgets import QApplication, QWidget
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from ui_helper import *

SERVER_URL = "https://wesee.strangled.net:3000"

class KeyManager(QWidget):
    def __init__(self, email=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Key Manager")
        self.handle_submit(email)
        
    def handle_submit(self, identity):
        email = identity
        # First check if key exists locally
        user_key_file = f"{email}_master_key_token.json"
        if os.path.exists(user_key_file):
            try:
                with open(user_key_file, 'r') as f:
                    key_data = json.load(f)
                    if key_data.get("email") == email and "encrypted_master_key" in key_data:
                        self.enc_umk = key_data["encrypted_master_key"]
                        return # ✅ Exit early if local key found
            except (json.JSONDecodeError, base64.binascii.Error, Exception):
                pass # Handle malformed JSON silently
                
        # Proceed with fetch or registration
        if self.check_user_registered(email):
            key = self.fetch_key(email)
            if key:
                self.store_key_locally(email, key)
                self.enc_umk = key
                dialog = CustomSuccessDialog("Success", "Key fetched and stored locally.", parent=self)
                dialog.exec()
            else:
                dialog = CustomErrorDialog("Error", "Failed to fetch the key.", parent=self)
                dialog.exec()
        else:
            # Use custom message box
            dialog = CustomMessageBox(
                "Register", 
                "User not found. Would you like to register?",
                parent=self,
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = self.get_valid_password()
                if password:
                    secret_key = os.urandom(32)
                    self.enc_umk = self.encrypt_secret_key(secret_key, password)
                    if self.register_user(email, self.enc_umk):
                        self.store_key_locally(email, self.enc_umk)
                        dialog = CustomSuccessDialog("Registered", "Account created and key stored locally.", parent=self)
                        dialog.exec()
                    else:
                        dialog = CustomErrorDialog("Error", "Registration failed.", parent=self)
                        dialog.exec()
                else:
                    dialog = CustomSuccessDialog("Cancelled", "Registration cancelled.", parent=self)
                    dialog.exec()
    
    def get_valid_password(self):
        """Get a strong password using the custom dialog"""
        dialog = PasswordDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return None
    

    def check_user_registered(self, email):
        try:
            response = requests.get(f"{SERVER_URL}/get_key/{email}")
            return response.status_code == 200
        except Exception as e:
            dialog = CustomErrorDialog("Server error", str({e}), parent=self)
            dialog.exec()
            return False

    def fetch_key(self, email):
        try:
            response = requests.get(f"{SERVER_URL}/get_key/{email}")
            if response.status_code == 200:
                data = response.json()
                return data['encrypted_master_key']
            return None
        except Exception as e:
            dialog = CustomErrorDialog("Fetch error", str({e}), parent=self)
            dialog.exec()
            return None

    def register_user(self, email, encrypted_master_key):
        try:
            payload = {
                "username": email,
                "encrypted_master_key": encrypted_master_key
            }
            response = requests.post(f"{SERVER_URL}/register", json=payload)
            return response.status_code == 200
        except Exception as e:
            dialog = CustomErrorDialog("Registration error", str({e}), parent=self)
            dialog.exec()
            return False


    def encrypt_secret_key(self, secret_key: bytes, password: str) -> str:
        """Encrypts the secret key using password-derived key."""
        salt = os.urandom(16)  # Random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        encrypted_secret = fernet.encrypt(secret_key)
        # Store salt along with encrypted data
        return base64.b64encode(salt + encrypted_secret).decode('utf-8')

    def store_key_locally(self, email, encrypted_master_key):
        filename = f"{email}_master_key_token.json"
        with open(filename, 'w') as f:
            json.dump({
                "email": email,
                "encrypted_master_key": encrypted_master_key
            }, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = KeyManager()
    manager.show()
    sys.exit(app.exec())

