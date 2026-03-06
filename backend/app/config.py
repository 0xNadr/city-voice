from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "CityVoice API"
    debug: bool = True

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"

    # Data paths
    opening_hours_path: str = "./data/opening_hours.json"
    knowledge_base_path: str = "./data/knowledge_base"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
