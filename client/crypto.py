import os, requests, hashlib, json, base64, requests
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.ibenc.ibenc_waters09_z import DSE09_z
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap
from ui_helper import *

GROUP = PairingGroup('MNT224')
IBE = DSE09_z(GROUP)

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Secure Access")
        self.setFixedSize(400, 280)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container frame with rounded corners
        self.container = QFrame()
        self.container.setObjectName("containerFrame")
        self.container.setStyleSheet("""
            #containerFrame {
                background-color: #2c3e50;
                border-radius: 10px;
            }
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with lock icon
        header_layout = QHBoxLayout()
        
        # Use actual lock icon image with proper sizing and transparent background
        lock_icon = QLabel()
        lock_icon.setStyleSheet("background: transparent;")
        lock_pixmap = QPixmap("Icon/lock_icon.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                                      Qt.TransformationMode.SmoothTransformation)
        lock_icon.setPixmap(lock_pixmap)
        header_layout.addWidget(lock_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addLayout(header_layout)
        
        # Title with transparent background
        title_label = QLabel("User Master Key Decryption")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Description with transparent background
        desc_label = QLabel("Please enter your password to decrypt the UMK.")
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #bdc3c7; background: transparent;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        container_layout.addWidget(desc_label)
        
        # Password field with show/hide toggle in a horizontal layout
        password_layout = QHBoxLayout()
        password_layout.setSpacing(0)
        
        # Password field with styling
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setMinimumHeight(40)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #34495e;
                border-radius: 5px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 5px 10px;
                background-color: #34495e;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        password_layout.addWidget(self.password_edit)
        
        # Show/hide password button
        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setIcon(QIcon("Icon/eye-off.png")) 
        self.toggle_password_button.setObjectName("toggle_button")
        self.toggle_password_button.setFixedSize(40, 40)
        self.toggle_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_button.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #bdc3c7;
                border: 1px solid #34495e;
                border-left: none;
                border-radius: 5px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d5268;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        self.toggle_password_button.clicked.connect(lambda: self.toggle_password_visibility(self.password_edit))
        password_layout.addWidget(self.toggle_password_button)
        
        container_layout.addLayout(password_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #455a64;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #546e7a;
            }
            QPushButton:pressed {
                background-color: #37474f;
            }
        """)
        buttons_layout.addWidget(self.cancel_button)
        
        # Decrypt button
        self.decrypt_button = QPushButton("Decrypt")
        self.decrypt_button.setMinimumHeight(40)
        self.decrypt_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6da8;
            }
        """)
        buttons_layout.addWidget(self.decrypt_button)
        
        container_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.container)
        
        # Connect signals
        self.cancel_button.clicked.connect(self.reject)
        self.decrypt_button.clicked.connect(self.accept)
        self.password_edit.returnPressed.connect(self.accept)
        
        # Set focus to password field
        self.password_edit.setFocus()
    
    def get_password(self):
        return self.password_edit.text()
    
    def toggle_password_visibility(self, field):
        """Toggle password visibility for a specific field"""
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            if field == self.password_edit:
                self.toggle_password_button.setIcon(QIcon("Icon/eye.png"))
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            if field == self.password_edit:
                self.toggle_password_button.setIcon(QIcon("Icon/eye-off.png"))
    
    # For dragging the window
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class SecretKeyDecryptor:
    def __init__(self, parent_widget):
        """
        :param parent_widget: QWidget used as the parent for dialogs (e.g., self in PyQt classes)
        """
        self.parent = parent_widget
    
    def decrypt(self, encrypted_data_b64: str):
        """
        Prompt user for password and decrypt the encrypted secret key.
        :param encrypted_data_b64: base64-encoded string of (salt + fernet_encrypted_key)
        :return: decrypted secret key (bytes) or None
        """
        try:
            encrypted_data = base64.b64decode(encrypted_data_b64)
            salt = encrypted_data[:16]
            encrypted_blob = encrypted_data[16:]
            
            # Use our custom password dialog instead of QInputDialog
            dialog = PasswordDialog(self.parent)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.get_password()
                if not password:
                    dialog = CustomErrorDialog("Decryption Failed", "Password cannot be empty", self.parent)
                    dialog.exec_()
                    return None
            else:
                return None  # User canceled
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100_000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            secret_key = fernet.decrypt(encrypted_blob)
            return secret_key
            
        except Exception as e:
            dialog = CustomErrorDialog(self.parent, "Decryption Failed", {str(e)})
            dialog.exec_()
            return None


def derive_file_key(master_key, context):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=context.encode(),
        backend=default_backend()
    )
    return hkdf.derive(master_key)

def encrypt_file(in_path, out_path, key):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    with open(in_path, 'rb') as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    with open(out_path, 'wb') as f:
        f.write(nonce + ciphertext)

def decrypt_file(enc_path, out_path, key):
    with open(enc_path, 'rb') as f:
        nonce = f.read(12)
        ciphertext = f.read()
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    with open(out_path, 'wb') as f:
        f.write(plaintext)

def serialize_dict(group, data):
    serialized = {}
    for key, value in data.items():
        serialized[key] = group.serialize(value).hex()
    return serialized

def deserialize_dict(group, data_serialized):
    deserialized = {}
    for key, value in data_serialized.items():
        if isinstance(key, str) and key.isdigit():
            k = int(key)
        else:
            k = key
        deserialized[k] = group.deserialize(bytes.fromhex(value))
    return deserialized

def deserialize_sk(group, sk_serialized):
    deserialized = {}
    deserialized['ID'] = group.deserialize(bytes.fromhex(sk_serialized['ID']))
    deserialized['D'] = {}
    for k, v in sk_serialized['D'].items():
        deserialized['D'][int(k)] = group.deserialize(bytes.fromhex(v))
    deserialized['K'] = group.deserialize(bytes.fromhex(sk_serialized['K']))
    deserialized['tag_k'] = group.deserialize(bytes.fromhex(sk_serialized['tag_k']))
    return deserialized

def encrypt_file_key(file_name, email, master_key):
    file_name = file_name[:-4] if file_name.endswith(".enc") else file_name
    context = f"{file_name}"
    file_key = derive_file_key(master_key, context)

    # Get master public key from remote
    response = requests.get("https://wesee.strangled.net:3000/get-master-public-key")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch public key: {response.text}")

    mpk_serialized = response.json()["master_public_key"]
    mpk = deserialize_dict(GROUP, mpk_serialized)
    msg = GROUP.random(GT)

    ciphertext = IBE.encrypt(mpk, msg, email)
    aes_key_mask = hashlib.sha256(str(msg).encode()).digest()
    ciphertext_serialized = serialize_dict(GROUP, ciphertext)

    masked_key = bytes(a ^ b for a, b in zip(file_key, aes_key_mask))
    ciphertext_b64 = base64.b64encode(json.dumps(ciphertext_serialized).encode()).decode()
    masked_key_b64 = base64.b64encode(masked_key).decode()

    final_json = json.dumps({
        "ciphertext": ciphertext_b64,
        "masked_key": masked_key_b64
    })

    return base64.b64encode(final_json.encode()).decode()


def decrypt_file_key(gmail_key):
     # 1. Base64-decode and parse JSON
    final_json = base64.b64decode(gmail_key).decode()
    payload = json.loads(final_json)

    ciphertext_b64 = payload["ciphertext"]
    masked_key_b64 = payload["masked_key"]

    from auth import get_keycloak_token
    token = get_keycloak_token()
    access_token = token["access_token"]

    # Send request
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://wesee.strangled.net:3000/get-client-secret-key", headers=headers)
    if response.status_code == 200:
        data = response.json()
        sk_serialized = data["client_secret_key"]
        sk = deserialize_sk(GROUP, sk_serialized)
        ciphertext_json = base64.b64decode(ciphertext_b64).decode()
        ciphertext_serialized = json.loads(ciphertext_json)
        ciphertext = deserialize_dict(GROUP, ciphertext_serialized)
        recovered_msg = IBE.decrypt(ciphertext, sk)
        aes_key_mask = hashlib.sha256(str(recovered_msg).encode()).digest()
        # Step 5: Decode masked key
        masked_key = base64.b64decode(masked_key_b64)
        file_key = bytes(a ^ b for a, b in zip(masked_key, aes_key_mask))
        return file_key
    else:
        print("Failed to get master public key:", response.status_code, response.text)
