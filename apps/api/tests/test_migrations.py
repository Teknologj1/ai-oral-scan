from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from ai_oral_scan.config import settings


def test_initial_migration_creates_expected_schema(tmp_path, monkeypatch):
    database_file = tmp_path / "migration.sqlite"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{database_file.as_posix()}")
    config = Config("alembic.ini")
    command.upgrade(config, "head")

    inspector = inspect(create_engine(settings.database_url))
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
