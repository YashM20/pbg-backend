from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    env: str = "dev"
    port: int = 8001

    # OCR pipeline
    ocr_device: str = "gpu:2"
    ocr_temp_dir: str = "cache/temp_uploads"

    # Sentry Configuration
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 1.0
    sentry_profile_session_sample_rate: float = 1.0
    sentry_profile_lifecycle: Literal["manual", "trace"] = "trace"
    sentry_send_default_pii: bool = True
    sentry_enable_logs: bool = True


settings = Settings()