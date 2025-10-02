import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    MAX_ACTIVE_TOKENS: int = int(os.getenv("MAX_ACTIVE_TOKENS", 5))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")  # Добавляем эту строку
    
    def __init__(self):
        if not self.SECRET_KEY or self.SECRET_KEY == "fallback-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in .env file")

settings = Settings()