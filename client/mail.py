import base64, re, os, base64
from auth import gmail_login
from crypto import decrypt_file_key
from googleapiclient.discovery import build

def save_cache(file_id, decrypted_key, user_id):
    # Folder structure: ./cache/{user_id}/
    folder_path = os.path.join('cache', user_id)
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist

    file_path = os.path.join(folder_path, file_id)

    with open(file_path, 'wb') as f:
        f.write(base64.b64encode(decrypted_key))

    print(f"🔒 Saved AES key for {file_id} under {folder_path}")

def load_cache(file_id, user_id):
    folder_path = os.path.join('cache', user_id)
    file_path = os.path.join(folder_path, file_id)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            encoded_key = f.read()
        decrypted_key = base64.b64decode(encoded_key)
        print(f"📂 Loaded AES key for {file_id} from {folder_path}")
        return decrypted_key

    return None

def extract_aes_key_from_gmail(file_id):
    creds = gmail_login()
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    user_id = profile['emailAddress']
    cached_key = load_cache(file_id, user_id)
    if cached_key:
        print(f"✅ Found AES key for {file_id} in cache.")
        return cached_key

    print(f"🔍 AES key for {file_id} not found in cache, searching Gmail...")

    page_token = None
    while True:
        results = service.users().messages().list(
            userId='me',
            q="subject:'Item shared with you'",
            maxResults=100,
            pageToken=page_token
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            break

        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            payload = msg_data.get('payload', {})
            parts = payload.get('parts', [])
            full_text = ""

            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    data = part["body"]["data"]
                    full_text = base64.urlsafe_b64decode(data).decode()

            # Search for the file ID
            match_id = re.search(r'File ID:\s*([a-zA-Z0-9_-]+)', full_text)
            if match_id and match_id.group(1) == file_id:
                # Search for the encrypted AES key
                pattern = r'-----BEGIN IBE CIPHERTEXT-----(.*?)-----END IBE CIPHERTEXT-----'
                match_key = re.search(pattern, full_text, re.DOTALL)

                if match_key:
                    encrypted_key_b64 = match_key.group(1).strip().replace('\n', '')
                    
                    decrypted_key = decrypt_file_key(encrypted_key_b64)
                    save_cache(file_id, decrypted_key, user_id)

                    print(f"✅ AES key for {file_id} extracted from Gmail and cached.")
                    return decrypted_key

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    print(f"❌ AES key not found in Gmail for file ID {file_id}.")
    return None
