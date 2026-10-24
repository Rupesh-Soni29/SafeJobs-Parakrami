import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "safejobs-secure-key-2026-xyz99")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "safejobs.db")
