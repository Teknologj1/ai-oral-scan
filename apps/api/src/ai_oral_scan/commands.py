import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select

from ai_oral_scan.db import SessionLocal
from ai_oral_scan.models import User
from ai_oral_scan.security import hash_password


def create_user() -> None:
    parser = argparse.ArgumentParser(description="Provision a local AI Oral Scan account")
    parser.add_argument("email")
    parser.add_argument("role", choices=["state_admin", "municipal_manager", "field_operator", "dentist", "analyst"])
    parser.add_argument("scope_id")
    parser.add_argument("--password", required=True, help="Unique password, at least 12 characters")
    args = parser.parse_args()
    if len(args.password) < 12:
        parser.error("password must have at least 12 characters")
    migration_config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(migration_config, "head")
    with SessionLocal() as db:
        email = args.email.lower()
        if db.scalar(select(User).where(User.email == email)):
            parser.error("account already exists")
        db.add(User(email=email, role=args.role, scope_id=args.scope_id, password_hash=hash_password(args.password)))
        db.commit()
    print(f"Created {args.role} account for {email}")


if __name__ == "__main__":
    create_user()
