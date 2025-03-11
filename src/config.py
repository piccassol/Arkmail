import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PDGmail API"
    
    # Database Connection
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pdgmail")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Mailchimp API (if using for emails)
    MAILCHIMP_API_KEY: str = os.getenv("MAILCHIMP_API_KEY", "")
    MAILCHIMP_SERVER_PREFIX: str = os.getenv("MAILCHIMP_SERVER_PREFIX", "")

    # SMTP Settings (for sending emails)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Redis for Celery (if needed for background tasks)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"  # Load environment variables from .env file

settings = Settings()
