from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai_oral_scan.db import Base, get_db
from ai_oral_scan.main import app
from ai_oral_scan.models import User
from ai_oral_scan.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db():
    with TestingSession() as session:
        yield session


app.dependency_overrides[get_db] = override_db


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        db.add(User(email="dentist@example.com", role="dentist", scope_id="municipality-1", password_hash=hash_password("correct-horse-battery")))
        db.add(User(email="inactive@example.com", role="state_admin", scope_id="state", is_active=False, password_hash=hash_password("correct-horse-battery")))
        db.commit()


def test_login_and_current_user():
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "correct-horse-battery"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        profile = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile.status_code == 200
        assert profile.json()["role"] == "dentist"
        assert profile.json()["scope_id"] == "municipality-1"


def test_invalid_password_and_inactive_user_are_rejected():
    with TestClient(app) as client:
        bad = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "wrong-password"})
        inactive = client.post("/api/v1/auth/login", json={"email": "inactive@example.com", "password": "correct-horse-battery"})
        assert bad.status_code == 401
        assert inactive.status_code == 401


def test_role_gate_denies_dentist_from_admin_route():
    with TestClient(app) as client:
        token = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "correct-horse-battery"}).json()["access_token"]
        response = client.get("/api/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


def test_missing_or_invalid_token_is_rejected():
    with TestClient(app) as client:
        assert client.get("/api/v1/auth/me").status_code == 401
        assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_public_registration_is_not_available():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "attacker@example.com", "password": "correct-horse-battery", "role": "state_admin"},
        )
        assert response.status_code == 404
