from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai_oral_scan.db import Base, get_db
from ai_oral_scan.main import app
from ai_oral_scan.models import Municipality, RoleAssignment, School, User
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
        db.add_all(
            [
                Municipality(id="municipality-1", ibge_code="1234567", name="Município Um", state_uf="SP"),
                Municipality(id="municipality-2", ibge_code="7654321", name="Município Dois", state_uf="SP"),
                School(id="school-1", municipality_id="municipality-1", name="Escola Um"),
                School(id="school-2", municipality_id="municipality-2", name="Escola Dois"),
                User(id="user-dentist", email="dentist@example.com", role="dentist", scope_id="municipality-1", password_hash=hash_password("correct-horse-battery")),
                User(id="user-inactive", email="inactive@example.com", role="state_admin", scope_id="state", is_active=False, password_hash=hash_password("correct-horse-battery")),
            ]
        )
        db.add_all(
            [
                RoleAssignment(user_id="user-dentist", role="dentist", scope_type="school", scope_id="school-1"),
                RoleAssignment(user_id="user-inactive", role="state_admin", scope_type="state", scope_id="*"),
            ]
        )
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


def test_refresh_rotates_tokens_and_revokes_the_previous_access_token():
    with TestClient(app) as client:
        initial = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "correct-horse-battery"}).json()
        rotated_response = client.post("/api/v1/auth/refresh", json={"refresh_token": initial["refresh_token"]})
        assert rotated_response.status_code == 200
        rotated = rotated_response.json()
        assert rotated["refresh_token"] != initial["refresh_token"]
        old_access = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {initial['access_token']}"})
        current_access = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {rotated['access_token']}"})
        old_refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": initial["refresh_token"]})
        assert old_access.status_code == 401
        assert current_access.status_code == 200
        assert old_refresh.status_code == 401


def test_logout_revokes_access_and_refresh_tokens():
    with TestClient(app) as client:
        tokens = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "correct-horse-battery"}).json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
        assert client.get("/api/v1/auth/me", headers=headers).status_code == 401
        assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_school_access_is_limited_to_assigned_territory():
    with TestClient(app) as client:
        tokens = client.post("/api/v1/auth/login", json={"email": "dentist@example.com", "password": "correct-horse-battery"}).json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        own_school = client.get("/api/v1/schools/school-1", headers=headers)
        other_school = client.get("/api/v1/schools/school-2", headers=headers)
        assert own_school.status_code == 200
        assert other_school.status_code == 404
