import os
import time
import hmac
import hashlib
import base64
import json
import sqlite3
import secrets
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

JWT_SECRET = os.getenv("FINAGENT_JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "FINAGENT_JWT_SECRET is not set. "
        "Set it before starting FINAGENT."
    )

if len(JWT_SECRET) < 32:
    raise RuntimeError(
        "FINAGENT_JWT_SECRET must contain at least 32 characters."
    )

JWT_TTL = int(os.getenv("FINAGENT_JWT_TTL_SECONDS", "1800"))

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

AUTH_DB = os.getenv(
    "FINAGENT_AUTH_DB",
    os.path.join(BASE_DIR, "data", "security", "auth.db")
)


# ============================================================
# ROLES AND PERMISSIONS
# ============================================================

ROLE_PERMISSIONS = {

    "ADMIN": {
        "*"
    },

    "FRAUD_ANALYST": {
        "customer:read",
        "transaction:read",
        "risk:read",
        "network:read",
        "policy:read",
        "evidence:read",
    },

    "INVESTIGATOR": {
        "customer:read",
        "transaction:read",
        "risk:read",
        "network:read",
        "policy:read",
        "evidence:read",
        "case:investigate",
        "report:generate",
    },

    "AUDITOR": {
        "customer:read",
        "transaction:read",
        "risk:read",
        "network:read",
        "policy:read",
        "evidence:read",
        "audit:read",
    }
}


# ============================================================
# DATABASE
# ============================================================

def init_auth_db():

    os.makedirs(
        os.path.dirname(AUTH_DB),
        exist_ok=True
    )

    conn = sqlite3.connect(AUTH_DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL,

            active INTEGER DEFAULT 1,

            created_at INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        310000
    )

    return (
        base64.b64encode(salt).decode()
        + "$"
        + base64.b64encode(password_hash).decode()
    )


def verify_password(
    password: str,
    stored_hash: str
) -> bool:

    salt_b64, hash_b64 = stored_hash.split("$")

    salt = base64.b64decode(salt_b64)

    expected_hash = base64.b64decode(hash_b64)

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        310000
    )

    return hmac.compare_digest(
        actual_hash,
        expected_hash
    )


# ============================================================
# JWT
# ============================================================

def base64url(data: bytes) -> str:

    return base64.urlsafe_b64encode(
        data
    ).rstrip(b"=").decode()


def create_token(
    username: str,
    role: str
) -> str:

    now = int(time.time())

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + JWT_TTL
    }

    header_encoded = base64url(
        json.dumps(
            header,
            separators=(",", ":")
        ).encode()
    )

    payload_encoded = base64url(
        json.dumps(
            payload,
            separators=(",", ":")
        ).encode()
    )

    message = (
        header_encoded
        + "."
        + payload_encoded
    )

    signature = hmac.new(
        JWT_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()

    signature_encoded = base64url(signature)

    return (
        message
        + "."
        + signature_encoded
    )


def decode_token(token: str):

    try:

        header_b64, payload_b64, signature_b64 = token.split(".")

        message = (
            header_b64
            + "."
            + payload_b64
        )

        expected_signature = hmac.new(
            JWT_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

        actual_signature = base64.urlsafe_b64decode(
            signature_b64 + "=="
        )

        if not hmac.compare_digest(
            expected_signature,
            actual_signature
        ):
            raise ValueError("Invalid signature")

        payload = json.loads(
            base64.urlsafe_b64decode(
                payload_b64 + "=="
            )
        )

        if payload["exp"] < int(time.time()):
            raise ValueError("Token expired")

        return payload

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ============================================================
# FASTAPI AUTHENTICATION
# ============================================================

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials =
        Depends(bearer_scheme)
):

    return decode_token(
        credentials.credentials
    )


# ============================================================
# PERMISSION CHECK
# ============================================================

def require_permission(permission: str):

    def checker(
        user=Depends(get_current_user)
    ):

        role = user.get("role")

        permissions = ROLE_PERMISSIONS.get(
            role,
            set()
        )

        if "*" not in permissions and permission not in permissions:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return checker


# ============================================================
# INITIALIZE
# ============================================================

init_auth_db()