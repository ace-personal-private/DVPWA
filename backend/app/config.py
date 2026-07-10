from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "sqlite:///./test.db"  # Default database URL
    # VULN-CWE-798: hardcoded fallback secret, matches .env.example verbatim
    jwt_secret: str = "changeme_local_dev_only"  # noqa: S105 -- VULN-CWE-798
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    env: str = "development"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# initialize settings
settings = Settings()
