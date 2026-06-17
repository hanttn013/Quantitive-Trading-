from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ProviderStatus = Literal["configured", "degraded"]


class Settings(BaseSettings):
    app_name: str = "AurumQuant API"
    app_version: str = "0.1.0"
    frontend_origin: str = "http://127.0.0.1:8080"
    database_url: str = "sqlite:///./aurumquant.db"
    deepseek_api_key: str = Field(default="", repr=False)
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    mt5_live_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def deepseek_status(self) -> ProviderStatus:
        return "configured" if self.deepseek_api_key else "degraded"


@lru_cache
def get_settings() -> Settings:
    return Settings()
