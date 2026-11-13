from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    app_name: str = "QA Job Agent"
    database_url: str = "sqlite:///./data/qa_jobs.db"
    scan_interval_minutes: int = 30
    request_timeout_seconds: int = 20
    max_jobs_per_source: int = 500
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
