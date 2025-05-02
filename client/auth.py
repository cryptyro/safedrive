# drivebuddy/auth.py

import os, time, json, requests, webbrowser
from urllib.parse import urlencode
from google.auth.exceptions import GoogleAuthError
from flask import Flask, request, render_template_string
from threading import Thread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from PyQt6.QtCore import QThread, pyqtSignal
from googleapiclient.discovery import build



DRIVE_TOKEN = 'gdrive_token.json'
GOOGLE_SECRET = 'client_secret.json'
SCOPE = ['openid', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

def get_user_info(creds):
    """Fetch user details using Google API"""
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    # Extract user details
    user_details = {
        "name": user_info['name'],
        "email": user_info['email'],
        "profile_pic": user_info['picture'], # Google provides a URL to the profile picture
        "token": creds.token
    }
    return user_details

class LoginWorker(QThread):
    login_success = pyqtSignal(object, dict)
    login_failed = pyqtSignal(str)

    def run(self):
        try:
            creds = app_login()
            if creds is None:
                self.login_failed.emit("Login was cancelled or failed.")
                return
            user_details = get_user_info(creds)
            self.login_success.emit(creds, user_details)
        except Exception as e:
            self.login_failed.emit(str(e))

def app_login():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_SECRET, SCOPE)
        creds = flow.run_local_server(port=0)
        # Save credentials
        with open(DRIVE_TOKEN, 'w') as token:
            token.write(creds.to_json())
        return creds
    except (GoogleAuthError, OSError, Exception) as e:
        print("Login failed or was cancelled:", str(e))
        return None



# This scope allows read-only Gmail access
MAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.readonly']
MAIL_TOKEN = 'gmail_token.json'

def gmail_login():
    creds = None

    # Load token if it exists
    if os.path.exists(MAIL_TOKEN):
        creds = Credentials.from_authorized_user_file(MAIL_TOKEN, MAIL_SCOPE)

    # If no token or token invalid/expired, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_SECRET, MAIL_SCOPE)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(MAIL_TOKEN, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds


# Configuration
KEYCLOAK_URL = "https://wesee.strangled.net:8443"
REALM = "mystwood"
CLIENT_ID = "drivebuddy"
CLIENT_SECRET = "yfawViW7vLdvVrIjwrH5bfTqTEFn52CI"
REDIRECT_URI = "http://localhost:8000/callback"
TOKEN_FILE = "keycloak_token.json"

# OAuth endpoints
AUTH_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

# Flask app to catch the redirect
app = Flask(__name__)
auth_code = None

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    
    # HTML template with embedded CSS and JavaScript
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Authentication Successful</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
                overflow: hidden;
            }
            .container {
                background-color: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
                max-width: 500px;
                animation: fadeIn 0.5s ease-out;
            }
            h1 {
                margin: 0 0 20px 0;
                font-weight: 600;
            }
            p {
                font-size: 18px;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .checkmark {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: block;
                stroke-width: 2;
                stroke: #4bb71b;
                stroke-miterlimit: 10;
                box-shadow: 0 0 20px #4bb71b;
                animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
                margin: 0 auto 20px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.2);
            }
            .checkmark__circle {
                stroke-dasharray: 166;
                stroke-dashoffset: 166;
                stroke-width: 2;
                stroke-miterlimit: 10;
                stroke: #4bb71b;
                fill: none;
                animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
            }
            .checkmark__check {
                transform-origin: 50% 50%;
                stroke-dasharray: 48;
                stroke-dashoffset: 48;
                animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
            }
            .countdown {
                font-size: 14px;
                margin-top: 20px;
                opacity: 0.7;
            }
            @keyframes stroke {
                100% {
                    stroke-dashoffset: 0;
                }
            }
            @keyframes scale {
                0%, 100% {
                    transform: none;
                }
                50% {
                    transform: scale3d(1.1, 1.1, 1);
                }
            }
            @keyframes fill {
                100% {
                    box-shadow: inset 0 0 0 30px rgba(255, 255, 255, 0.2);
                }
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .particles {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
            }
            .particle {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.5);
            }
            #redirect-message {
                display: none;
                margin-top: 20px;
                font-size: 16px;
                color: #ffffff;
                background-color: rgba(0, 0, 0, 0.1);
                padding: 10px;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="particles" id="particles-container"></div>
        <div class="container">
            <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/>
                <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
            </svg>
            <h1>Authentication Successful</h1>
            <p>Your account has been successfully authenticated.</p>
            <div class="countdown">This window will close in <span id="timer">3</span> seconds</div>
            <div id="redirect-message">
                If the window doesn't close automatically, you may close it now.
            </div>
        </div>

        <script>
            // Create floating particles for background effect
            function createParticles() {
                const particlesContainer = document.getElementById('particles-container');
                const particleCount = 30;
                
                for (let i = 0; i < particleCount; i++) {
                    const particle = document.createElement('div');
                    particle.classList.add('particle');
                    
                    // Random size between 3px and 20px
                    const size = Math.random() * 17 + 3;
                    particle.style.width = `${size}px`;
                    particle.style.height = `${size}px`;
                    
                    // Random position
                    particle.style.left = `${Math.random() * 100}%`;
                    particle.style.top = `${Math.random() * 100}%`;
                    
                    // Random transparency
                    particle.style.opacity = Math.random() * 0.5 + 0.1;
                    
                    // Create floating animation
                    const startX = Math.random() * 100;
                    const startY = Math.random() * 100;
                    const translateX = (Math.random() - 0.5) * 30;
                    const translateY = (Math.random() - 0.5) * 30;
                    const duration = Math.random() * 20 + 10;
                    const delay = Math.random() * 5;
                    
                    particle.style.transform = `translate(${startX}vw, ${startY}vh)`;
                    particle.style.transition = `transform ${duration}s ease-in-out ${delay}s`;
                    
                    setTimeout(() => {
                        particle.style.transform = `translate(${startX + translateX}vw, ${startY + translateY}vh)`;
                    }, 100);
                    
                    particlesContainer.appendChild(particle);
                }
            }
            
            // Countdown and auto-close
            let timeLeft = 3;
            const timerElement = document.getElementById('timer');
            const redirectMessage = document.getElementById('redirect-message');
            
            // Initialize window close functionality
            const closeWindow = function() {
                // Try multiple methods for closing
                try {
                    // Method 1: Try to close directly
                    window.close();
                    
                    // Method 2: If opened via window.open()
                    if (window.opener) {
                        window.opener.focus();
                    }
                    
                    // Show message after attempts
                    setTimeout(() => {
                        redirectMessage.style.display = 'block';
                    }, 300);
                } catch (e) {
                    console.error('Could not close window:', e);
                    redirectMessage.style.display = 'block';
                }
            };
            
            const countdownInterval = setInterval(() => {
                timeLeft -= 1;
                timerElement.textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    clearInterval(countdownInterval);
                    closeWindow();
                }
            }, 1000);
            
            // Initialize particles
            createParticles();
            
            // Add an event listener for clicks anywhere to help overcome popup blockers
            document.addEventListener('click', function() {
                if (timeLeft <= 0) {
                    closeWindow();
                }
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template)

def run_flask():
    app.run(port=8000)

def start_oauth_flow():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    webbrowser.open(url)

def exchange_code_for_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        print("Token saved to", TOKEN_FILE)
        return token_data
    else:
        print("Token request failed:", response.text)
        return None

def get_keycloak_token():
    global auth_code
    auth_code = None

    # Start Flask server in a background thread
    server = Thread(target=run_flask)
    server.daemon = True
    server.start()

    # Launch browser for user authentication
    start_oauth_flow()

    print("Waiting for authorization...")
    while auth_code is None:
        time.sleep(1)

    # Exchange code for token
    return exchange_code_for_token(auth_code)

