from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduGenie"
    environment: str = "development"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    # auto: use local LaMini when available, otherwise Gemini.
    # local: require local model.
    # gemini: always use Gemini.
    explanation_provider: str = "auto"
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"

    request_timeout_seconds: int = 90
    max_input_chars: int = 30000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
