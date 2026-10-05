from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ai_provider: Literal["mock", "openai"] = "mock"
    ai_api_key: SecretStr = SecretStr("")
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = Field(default="", max_length=200)
    ai_timeout_seconds: float = Field(default=30, ge=1, le=120)
    ai_max_output_tokens: int = Field(default=800, ge=100, le=2000)
    frontend_origin: str = "http://localhost:5173"

    @model_validator(mode="after")
    def validate_provider(self) -> "Settings":
        origin = urlsplit(self.frontend_origin)
        if (
            origin.scheme not in {"http", "https"}
            or not origin.hostname
            or origin.path not in {"", "/"}
            or origin.query
            or origin.fragment
            or origin.username
            or origin.password
        ):
            raise ValueError("FRONTEND_ORIGIN must be a single HTTP(S) origin")
        self.frontend_origin = self.frontend_origin.rstrip("/")
        if self.ai_provider == "openai":
            if not self.ai_api_key.get_secret_value().strip() or not self.ai_model.strip():
                raise ValueError("Real provider requires AI_API_KEY and AI_MODEL")
            url = urlsplit(self.ai_base_url)
            local = url.hostname in {"localhost", "127.0.0.1", "::1"}
            if (
                not url.hostname
                or (url.scheme != "https" and not (url.scheme == "http" and local))
                or url.username
                or url.password
                or url.query
                or url.fragment
            ):
                raise ValueError("AI_BASE_URL must use HTTPS (HTTP only on loopback)")
            self.ai_model = self.ai_model.strip()
        return self
