from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")

    postgres_db: str = Field(default="genomics_portal", alias="POSTGRES_DB")
    postgres_user: str = Field(default="genomics_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="genomics_pass", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    db_name: str | None = Field(default=None, alias="DB_NAME")
    db_user: str | None = Field(default=None, alias="DB_USER")
    db_password: str | None = Field(default=None, alias="DB_PASSWORD")
    db_host: str | None = Field(default=None, alias="DB_HOST")
    db_port: int | None = Field(default=None, alias="DB_PORT")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    streamlit_server_port: int = Field(default=8501, alias="STREAMLIT_SERVER_PORT")
    streamlit_server_headless: bool = Field(default=True, alias="STREAMLIT_SERVER_HEADLESS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def resolved_db_name(self) -> str:
        return self.db_name or self.postgres_db

    @property
    def resolved_db_user(self) -> str:
        return self.db_user or self.postgres_user

    @property
    def resolved_db_password(self) -> str:
        return self.db_password or self.postgres_password

    @property
    def resolved_db_host(self) -> str:
        return self.db_host or self.postgres_host

    @property
    def resolved_db_port(self) -> int:
        return self.db_port or self.postgres_port

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.resolved_db_user}:{self.resolved_db_password}"
            f"@{self.resolved_db_host}:{self.resolved_db_port}/{self.resolved_db_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()