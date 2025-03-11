import os
from pydantic_settings import BaseSettings

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
    MAILCHIMP_SERVER_PREFIX: str
