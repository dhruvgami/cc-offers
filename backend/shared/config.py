"""Configuration management for the application"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Database
    database_url: str = Field(default="sqlite:///./data/travel_discounts.db", env="DATABASE_URL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Scraping Configuration
    scraper_timeout: int = Field(default=30000, env="SCRAPER_TIMEOUT")
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        env="SCRAPER_USER_AGENT"
    )
    max_concurrent_scrapers: int = Field(default=5, env="MAX_CONCURRENT_SCRAPERS")
    scraper_delay_ms: int = Field(default=2000, env="SCRAPER_DELAY_MS")

    # AWS Configuration (for future deployment)
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
