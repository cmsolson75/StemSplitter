import os
from typing import List
from config_loader import config


class Settings:
    """Application configuration settings."""
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"
    
    # API Configuration - Use YAML config with env var fallbacks
    API_TITLE: str = config.get("api.title", "I AM SPLITTER API")
    API_DESCRIPTION: str = config.get("api.description", "AI-powered audio stem separation service")
    API_VERSION: str = config.get("api.version", "1.0.0")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS Configuration - Use YAML config
    CORS_ORIGINS: List[str] = config.get("api.cors_origins", ["http://localhost:3000"])
    
    # File Storage
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp")
    
    # Model Configuration - Use YAML config with env var fallbacks
    DEMUCS_MODEL: str = os.getenv("DEMUCS_MODEL", config.get("model.name", "htdemucs"))
    
    # GPU Configuration
    CUDA_VISIBLE_DEVICES: str = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    
    # Timeouts (seconds)
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 300))
    
    @property
    def docs_url(self) -> str:
        """Return docs URL only in development."""
        return "/docs" if self.DEBUG else None
    
    @property
    def redoc_url(self) -> str:
        """Return redoc URL only in development."""
        return "/redoc" if self.DEBUG else None
    
    @property
    def openapi_url(self) -> str:
        """Return OpenAPI URL only in development."""
        return "/openapi.json" if self.DEBUG else None


# Global settings instance
settings = Settings()