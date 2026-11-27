from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_oral_scan.db"
    jwt_secret: str = "development-only-change-this-secret"
    access_token_minutes: int = 20
    ai_clinical_enabled: bool = False

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[4] / ".env", extra="ignore")


settings = Settings()
