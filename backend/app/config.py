import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_BACKEND_DIR.parent

# Load .env from backend folder or project root
for candidate in [BASE_BACKEND_DIR / ".env", PROJECT_ROOT / ".env"]:
    if candidate.exists():
        load_dotenv(dotenv_path=candidate, override=False)
load_dotenv()

DEFAULT_DB_PATH = (PROJECT_ROOT / "nexora.db").as_posix()
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"

class Settings(BaseSettings):
    APP_NAME: str = "NEXORA AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL") or DEFAULT_DB_URL
    
    # AI Integration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    
    # Speech-to-Text: OpenAI Whisper
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "whisper-1")
    
    # Open-Meteo Weather API (free, no auth required)
    WEATHER_API_BASE: str = "https://api.open-meteo.com/v1/forecast"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
if settings.DATABASE_URL == "sqlite:///./nexora.db":
    settings.DATABASE_URL = DEFAULT_DB_URL
