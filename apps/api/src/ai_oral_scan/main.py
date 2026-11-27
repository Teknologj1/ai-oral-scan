from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_oral_scan.config import settings
from ai_oral_scan.db import get_db
from ai_oral_scan.models import User
from ai_oral_scan.security import create_access_token, verify_password

app = FastAPI(title="AI Oral Scan API", version="0.2.0")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
Db = Annotated[Session, Depends(get_db)]


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOutput(BaseModel):
    id: str
    email: str
    role: str
    scope_id: str | None


@app.get("/health")
def health():
    return {"status": "ok", "ai_clinical_enabled": settings.ai_clinical_enabled}


@app.post("/api/v1/auth/login", response_model=TokenOutput)
def login(data: LoginInput, db: Db):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_access_token(user.id, user.role, user.scope_id)}


def current_user(token: Annotated[str, Depends(oauth2)], db: Db) -> User:
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user = db.get(User, claims["sub"])
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive account")
    return user


@app.get("/api/v1/auth/me", response_model=UserOutput)
def me(user: Annotated[User, Depends(current_user)]):
    return user


@app.get("/api/v1/admin/ping")
def admin_ping(user: Annotated[User, Depends(current_user)]):
    if user.role != "state_admin":
        raise HTTPException(status_code=403, detail="Insufficient role")
    return {"status": "ok"}
