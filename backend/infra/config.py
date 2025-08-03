from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    gcs_bucket: str
    gcs_signed_url_expiry_minutes: int = 15
    ray_actor_name: str = "separation_actor"
    ray_namespace: str = "demucs-dev"
    model_name: str = "htdemucs"

    impersonation_account: str = ""  # optional for production
    env: str = "local"               # local or production

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()