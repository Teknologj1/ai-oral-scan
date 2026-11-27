from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from ai_oral_scan.config import settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: str, role: str, scope_id: str | None) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": user_id,
        "role": role,
        "scope": scope_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=ALGORITHM)
