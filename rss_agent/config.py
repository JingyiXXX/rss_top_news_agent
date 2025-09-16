"""
Configuration management for RSS News Agent
"""
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseSettings, validator

# Load environment variables
load_dotenv()


class Config(BaseSettings):
    """Configuration settings for the RSS News Agent"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Email Configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    email_user: str = os.getenv("EMAIL_USER", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    to_email: str = os.getenv("TO_EMAIL", "")
    
    # RSS Feed Configuration
    rss_feeds: str = os.getenv("RSS_FEEDS", "")
    
    # Schedule Configuration
    schedule_hour: int = int(os.getenv("SCHEDULE_HOUR", "9"))
    schedule_minute: int = int(os.getenv("SCHEDULE_MINUTE", "0"))
    
    # News Processing Configuration
    max_articles_per_run: int = int(os.getenv("MAX_ARTICLES_PER_RUN", "10"))
    min_viral_score: float = float(os.getenv("MIN_VIRAL_SCORE", "0.7"))
    
    @validator("rss_feeds")
    def parse_rss_feeds(cls, v) -> List[str]:
        """Parse comma-separated RSS feed URLs"""
        if not v:
            return []
        return [url.strip() for url in v.split(",") if url.strip()]
    
    class Config:
        env_file = ".env"


# Create configuration instance with validation disabled for empty values
try:
    config = Config()
    # Convert rss_feeds string to list if needed
    if isinstance(config.rss_feeds, str):
        config.rss_feeds = [url.strip() for url in config.rss_feeds.split(",") if url.strip()]
except Exception:
    # Fallback configuration for testing
    class FallbackConfig:
        openai_api_key = ""
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_user = ""
        email_password = ""
        to_email = ""
        rss_feeds = []
        schedule_hour = 9
        schedule_minute = 0
        max_articles_per_run = 10
        min_viral_score = 0.7
    
    config = FallbackConfig()