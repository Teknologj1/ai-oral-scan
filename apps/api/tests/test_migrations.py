from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from ai_oral_scan.config import settings


def test_initial_migration_creates_expected_schema(tmp_path, monkeypatch):
    database_file = tmp_path / "migration.sqlite"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{database_file.as_posix()}")
    config = Config("alembic.ini")
    command.upgrade(config, "0fd0c0f0cad3")
    engine = create_engine(settings.database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id, email, password_hash, role, scope_id, is_active, created_at) "
                "VALUES ('legacy-user', 'legacy@example.com', 'hash', 'municipal_manager', "
                "'municipality-legacy', 1, '2026-01-01T00:00:00')"
            )
        )
    command.upgrade(config, "head")

    inspector = inspect(engine)
    assert {
        "users",
        "municipalities",
        "regions",
        "schools",
        "campaigns",
        "student_identities",
        "student_subjects",
        "screenings",
        "audit_events",
        "alembic_version",
    }.issubset(set(inspector.get_table_names()))
    with engine.connect() as connection:
        role_scope = connection.execute(
            text("SELECT role, scope_type, scope_id FROM role_assignments WHERE user_id='legacy-user'")
        ).one()
    assert role_scope == ("municipal_manager", "municipality", "municipality-legacy")
    engine.dispose()
