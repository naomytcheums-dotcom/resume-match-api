import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""

    api_access_key: str = ""

    # Stored as a plain string (not list[str]) so pydantic-settings never
    # attempts to JSON-decode the raw env var itself — that step runs before
    # any custom validator and errors out on non-JSON values like "*". We
    # parse it ourselves in cors_origins below.
    cors_origins_raw: str = Field("*", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        text = self.cors_origins_raw.strip()
        if text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in text.split(",") if origin.strip()]


settings = Settings()
