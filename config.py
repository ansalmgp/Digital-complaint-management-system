import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'complaint-management-system-secret-key-12345')
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Database configurations
    # If DATABASE_URL is set (e.g., postgresql://username:password@localhost:5432/dbname), use ShaktiDB
    # Otherwise, fall back to SQLite for local development out-of-the-box
    DATABASE_URL = os.environ.get('DATABASE_URL', None)
    
    # SQLite fallback database file path
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'database', 'complaints.db')
