import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def validate_config():
    required_env_vars = ['FLASK_SECRET_KEY', 'DATABASE_URL']
    for var in required_env_vars:
        if not os.getenv(var):
            if os.getenv("FLASK_ENV") == "production":
                raise RuntimeError(f"Critical Error: {var} is not set in Production!")
            logger.warning(f"Warning: Environment variable '{var}' is not set. Using default values.")

validate_config()

class Config:
    """Base configuration with shared settings."""
    
    # Flask configurations
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'default_weather_key')
    SPEECH_API_KEY = os.getenv('SPEECH_API_KEY', 'default_speechkey')
    SPEECH_REGION = os.getenv('SPEECH_REGION', 'default_region')
    
    # Database Configuration - Ensures the correct SQLite path is always used
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "../database/TCC.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Session Configuration
    SESSION_TYPE = 'filesystem'  # Use filesystem-based sessions

    # File Paths
    PROJECT_FILE = os.path.join(BASE_DIR, '../data/project.csv')
    WORKERS_FILE = os.path.join(BASE_DIR, '../data/workers.csv')
    EQUIPMENT_FILE = os.path.join(BASE_DIR, '../data/equipment.csv')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ACTIVITY_CODES_FILE = os.path.join(BASE_DIR, '../data/activity_codes.csv')
    MATERIALS_FILE = os.path.join(BASE_DIR, '../data/materials.csv')
    PICTURES_FILE = os.path.join(BASE_DIR, '../data/pictures.csv')
    SUBCONTRACTORS_FILE = os.path.join(BASE_DIR, '../data/subcontractors.csv')
    DATA_FILE_PATH = os.path.join(BASE_DIR, '../data/daily_report_data.csv')

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/TCC.db'  # Ensures the correct DB is used

class TestingConfig(Config):
    """Configuration for running unit tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Uses an in-memory DB for tests

class ProductionConfig(Config):
    """Configuration for production environment."""
    # 1) Secret key for sessions & CSRF
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "fallback-dev-key")
    # 2) Database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///local-dev.db"  # fallback for local dev only
    )
    # 3) Whether to run builds during deployment
    #    (Azure’s default is to set SCM_DO_BUILD_DURING_DEPLOYMENT)
    DO_BUILD = os.environ.get("SCM_DO_BUILD_DURING_DEPLOYMENT", "false").lower() == "true"

     # 4) Your Speech API creds (note: fix spelling to match Azure)
    SPEECH_API_KEY    = os.environ.get("Speach_API_key")
    SPEECH_REGION     = os.environ.get("Speach_region")

     # 5) Weather API key
    WEATHER_API_KEY   = os.environ.get("WEATHER_API_KEY")

# Print or log the database path to verify it's correct
logger.info(f"Config loaded. Using database: {Config.SQLALCHEMY_DATABASE_URI}")
