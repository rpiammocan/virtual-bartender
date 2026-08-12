from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/bartender.db"
    backups_path: str = "./backups"
    media_path: str = "../data/images"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

if settings.database_url.startswith("sqlite:///./"):
    Path("./data").mkdir(parents=True, exist_ok=True)
Path(settings.backups_path).mkdir(parents=True, exist_ok=True)
