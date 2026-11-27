from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_oral_scan.config import settings
from ai_oral_scan.db import get_db
from ai_oral_scan.models import (
    AuditEvent,
    AuthSession,
    Municipality,
    RoleAssignment,
    School,
    User,
    utcnow,
)
from ai_oral_scan.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)

app = FastAPI(title="AI Oral Scan API", version="0.3.0")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
Db = Annotated[Session, Depends(get_db)]


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refresh_token: str


class TokenOutput(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOutput(BaseModel):
    id: str
    email: str
    role: str
    scope_id: str | None


class SchoolOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    municipality_id: str


@dataclass
class CurrentAuth:
    user: User
    session: AuthSession
    assignments: list[RoleAssignment]


def _session_expired(session: AuthSession, now: datetime) -> bool:
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at <= now


def _issue_tokens(user: User, session: AuthSession, refresh_token: str) -> TokenOutput:
    access_token, jti = create_access_token(user.id, session.id)
    session.access_jti = jti
    session.refresh_token_hash = hash_refresh_token(refresh_token)
    session.expires_at = utcnow() + timedelta(days=settings.refresh_token_days)
    return TokenOutput(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


@app.get("/health")
def health():
    return {"status": "ok", "ai_clinical_enabled": settings.ai_clinical_enabled}


@app.post("/api/v1/auth/login", response_model=TokenOutput)
def login(data: LoginInput, db: Db):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    assignments = db.scalars(
        select(RoleAssignment).where(RoleAssignment.user_id == user.id, RoleAssignment.is_active.is_(True))
    ).all()
    if not assignments:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active role assignment")

    session_id = str(uuid4())
    refresh_token = create_refresh_token()
    session = AuthSession(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        access_jti="pending",
        expires_at=utcnow() + timedelta(days=settings.refresh_token_days),
    )
    access_token, session.access_jti = create_access_token(user.id, session.id)
    db.add(session)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="auth.login",
            resource_type="auth_session",
            resource_id=session.id,
            outcome="success",
        )
    )
    db.commit()
    return TokenOutput(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
    )


def current_auth(token: Annotated[str, Depends(oauth2)], db: Db) -> CurrentAuth:
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user = db.get(User, claims["sub"])
        session = db.get(AuthSession, claims["sid"])
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None
    if (
        user is None
        or not user.is_active
        or session is None
        or session.user_id != user.id
        or session.revoked_at is not None
        or _session_expired(session, utcnow())
        or claims.get("jti") != session.access_jti
    ):
        raise HTTPException(status_code=401, detail="Invalid or revoked session")
    assignments = db.scalars(
        select(RoleAssignment).where(RoleAssignment.user_id == user.id, RoleAssignment.is_active.is_(True))
    ).all()
    if not assignments:
        raise HTTPException(status_code=403, detail="No active role assignment")
    return CurrentAuth(user=user, session=session, assignments=list(assignments))


@app.post("/api/v1/auth/refresh", response_model=TokenOutput)
def refresh(data: RefreshInput, db: Db):
    session = db.scalar(
        select(AuthSession).where(AuthSession.refresh_token_hash == hash_refresh_token(data.refresh_token))
    )
    now = utcnow()
    if session is None or session.revoked_at is not None or _session_expired(session, now):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive account")
    assignments = db.scalars(
        select(RoleAssignment).where(RoleAssignment.user_id == user.id, RoleAssignment.is_active.is_(True))
    ).all()
    if not assignments:
        session.revoked_at = now
        db.commit()
        raise HTTPException(status_code=403, detail="No active role assignment")
    replacement_refresh = create_refresh_token()
    tokens = _issue_tokens(user, session, replacement_refresh)
    db.add(
        AuditEvent(
            actor_id=user.id,
            action="auth.refresh",
            resource_type="auth_session",
            resource_id=session.id,
            outcome="success",
        )
    )
    db.commit()
    return tokens


@app.post("/api/v1/auth/logout", status_code=204)
def logout(auth: Annotated[CurrentAuth, Depends(current_auth)], db: Db):
    now = utcnow()
    auth.session.revoked_at = now
    db.add(
        AuditEvent(
            actor_id=auth.user.id,
            action="auth.logout",
            resource_type="auth_session",
            resource_id=auth.session.id,
            outcome="success",
        )
    )
    db.commit()


@app.get("/api/v1/auth/me", response_model=UserOutput)
def me(auth: Annotated[CurrentAuth, Depends(current_auth)]):
    return auth.user


@app.get("/api/v1/admin/ping")
def admin_ping(auth: Annotated[CurrentAuth, Depends(current_auth)]):
    if not any(assignment.role == "state_admin" for assignment in auth.assignments):
        raise HTTPException(status_code=403, detail="Insufficient role")
    return {"status": "ok"}


@app.get("/api/v1/schools/{school_id}", response_model=SchoolOutput)
def get_school(school_id: str, auth: Annotated[CurrentAuth, Depends(current_auth)], db: Db):
    school = db.get(School, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="School not found")
    municipality = db.get(Municipality, school.municipality_id)
    state_uf = municipality.state_uf if municipality else None
    permitted = any(
        assignment.is_active
        and (
            (assignment.scope_type == "school" and assignment.scope_id == school.id)
            or (assignment.scope_type == "municipality" and assignment.scope_id == school.municipality_id)
            or (
                assignment.scope_type == "state"
                and assignment.scope_id in {"*", "state", state_uf}
            )
        )
        for assignment in auth.assignments
    )
    if not permitted:
        # Hide resource existence from callers outside its authorized territory.
        raise HTTPException(status_code=404, detail="School not found")
    return school
