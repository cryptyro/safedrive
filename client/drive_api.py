# drivebuddy/drive_api.py

import os
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from mail import *
from crypto import *

def list_owned_by_me(drive_service):
    results = drive_service.files().list(
        q="'me' in owners and trashed = false",
        pageSize=20,
        fields="files(id, name, mimeType, size, modifiedTime, shared)"
    ).execute()
    files = results.get('files', [])
    
    for file in files:
        file['owned_by_me'] = True
        file['shared'] =  False  # Ensure 'shared' key exists

    return files


def list_shared_with_me(drive_service):
    results = drive_service.files().list(
        q="sharedWithMe",
        fields="files(id, name, mimeType, size, modifiedTime)"
    ).execute()
    files = results.get('files', [])

    for file in files:
        file['shared'] = True
        file['owned_by_me'] = False  # Explicitly set

    return files


def search_drive_files(drive_service, search_text):
    query = f"name contains '{search_text}' and trashed = false"
    results = drive_service.files().list(
        q=query,
        pageSize=20,
        fields="files(id, name, mimeType, size, modifiedTime, shared)"
    ).execute()
    return results.get('files', [])


def upload_file(drive_service, file_path, master_key):
    file_name = os.path.basename(file_path)
    context = f"{file_name}"
    
    file_key = derive_file_key(master_key, context)
    enc_path = file_path + ".enc"
    encrypt_file(file_path, enc_path, file_key)

    file_metadata = {'name': file_name + ".enc"}
    media = MediaFileUpload(enc_path, mimetype="application/octet-stream", resumable=True)

    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name'
    ).execute()
    
    os.remove(enc_path)
    return uploaded


def download_file_core(drive_service, file_id, is_shared, save_path, master_key):
    """Download and decrypt a file using either a shared key or master key."""
    enc_path = save_path + ".downloaded"

    # Download encrypted file
    request = drive_service.files().get_media(fileId=file_id)
    with open(enc_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    # Handle .enc extension
    file_name = os.path.basename(save_path)
    if file_name.endswith(".enc"):
        file_name = file_name[:-4]
        save_path = os.path.join(os.path.dirname(save_path), file_name)

    # Derive AES key
    if is_shared:
        file_key = extract_aes_key_from_gmail(file_id)
    else:
        context = f"{file_name}"
        file_key = derive_file_key(master_key, context)
    print(f"File key: {file_key}")
    decrypt_file(enc_path, save_path, file_key)
    os.remove(enc_path)

    return save_path



def share_file(drive_service, file_id, file_name, email, master_key):
    encoded_key = encrypt_file_key(file_name, email, master_key)
    email_msg = f"""Encrypted file is Shared.

File ID: {file_id}
-----BEGIN IBE CIPHERTEXT-----
{encoded_key}
-----END IBE CIPHERTEXT-----
"""

    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email
    }

    return drive_service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id',
        sendNotificationEmail=True,
        emailMessage=email_msg
    ).execute()


def delete_drive_file(drive_service, file_id):
    try:
        drive_service.files().delete(fileId=file_id).execute()
    except Exception as e:
        raise Exception(f"Failed to delete file with ID: {file_id}. Error: {e}")


def rename_drive_file(drive_service, file_id, new_name):
    try:
        file_metadata = {
            'name': new_name
        }
        drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields="id, name"
        ).execute()
    except Exception as e:
        raise Exception(f"Failed to rename file with ID: {file_id}. Error: {e}")

