from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import sqlite3
from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.ibenc.ibenc_waters09_z import DSE09_z
from jose import jwt
import requests

app = FastAPI()

# ---------- DATABASE SETUP ----------
DATABASE = "keys.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            encrypted_master_key TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- IBE SETUP ----------
GROUP = PairingGroup('MNT224')
IBE = DSE09_z(GROUP)
mpk, msk = IBE.setup()

def serialize_dict(group, data):
    return {k: group.serialize(v).hex() for k, v in data.items()}

def serialize_sk(group, sk):
    return {
        'ID': group.serialize(sk['ID']).hex(),
        'D': {str(k): group.serialize(v).hex() for k, v in sk['D'].items()},
        'K': group.serialize(sk['K']).hex(),
        'tag_k': group.serialize(sk['tag_k']).hex()
    }

mpk_serialized = serialize_dict(GROUP, mpk)

# ---------- MODELS ----------
class RegisterRequest(BaseModel):
    username: str
    encrypted_master_key: str

class GetKeyResponse(BaseModel):
    username: str
    encrypted_master_key: str

# ---------- DB FUNCTIONS ----------
def insert_user(username: str, encrypted_master_key: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, encrypted_master_key) VALUES (?, ?)",
            (username, encrypted_master_key)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_encrypted_key(username: str) -> Optional[str]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT encrypted_master_key FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# ---------- KEYCLOAK CONFIG ----------
KEYCLOAK_URL = "https://wesee.strangled.net:8443"
REALM = "mystwood"
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
EXPECTED_CLIENT_ID = "drivebuddy"

def verify_token(token: str):
    try:
        jwks = requests.get(JWKS_URL).json()
        kid = jwt.get_unverified_header(token).get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise Exception("Signing key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        if payload.get("azp") != EXPECTED_CLIENT_ID:
            raise Exception("Invalid azp")

        return payload
    except Exception as e:
        print("Token validation failed:", e)
        return None

# ---------- API ENDPOINTS ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/register")
def register_user(request: RegisterRequest):
    if insert_user(request.username, request.encrypted_master_key):
        return {"message": "User registered successfully."}
    else:
        raise HTTPException(status_code=400, detail="User already exists.")

@app.get("/get_key/{username}", response_model=GetKeyResponse)
def get_encrypted_master_key(username: str):
    encrypted_key = get_user_encrypted_key(username)
    if encrypted_key:
        return {"username": username, "encrypted_master_key": encrypted_key}
    else:
        raise HTTPException(status_code=404, detail="User not found.")

@app.get("/get-master-public-key")
def get_master_public_key():
    return {"master_public_key": mpk_serialized}

@app.get("/get-client-secret-key")
def get_client_secret_key(Authorization: str = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = Authorization.split(" ")[1]
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    identity = user_info.get("email")
    if not identity:
        raise HTTPException(status_code=400, detail="Email not found in token")

    sk = IBE.keygen(mpk, msk, identity)
    return {"client_secret_key": serialize_sk(GROUP, sk)}

# ---------- RUN ----------
# Use with: uvicorn finalserver:app --reload --host 0.0.0.0 --port 3000 --ssl-keyfile=server-key.pem --ssl-certfile=server-cert.pem
