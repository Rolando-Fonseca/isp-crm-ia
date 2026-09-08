from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    meta_whatsapp_token: str = ""
    meta_phone_number_id: str = ""
    meta_graph_api_version: str = "v22.0"
    meta_webhook_verify_token: str
    meta_app_secret: str

    crm_api_url: str = "http://localhost:3002"
    crm_internal_api_key: str

    @property
    def whatsapp_configured(self) -> bool:
        return bool(self.meta_whatsapp_token and self.meta_phone_number_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()
