import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Validate required environment variables in production
def validate_config():
    required_env_vars = ['FLASK_SECRET_KEY', 'DATABASE_URL']
    for var in required_env_vars:
        if not os.getenv(var):
            if os.getenv("FLASK_ENV") == "production":
                raise RuntimeError(f"Critical Error: {var} is not set in Production!")
            logger.warning(f"Environment variable '{var}' is not set. Using default values.")

validate_config()

# ----------------------------------------
# Base Config
# ----------------------------------------
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'default_weather_key')
    SPEECH_API_KEY = os.getenv('SPEECH_API_KEY', 'default_speechkey')
    SPEECH_REGION = os.getenv('SPEECH_REGION', 'default_region')

    # Default DB fallback
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "../database/TCC.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'

    # Common file paths
    PROJECT_FILE = os.path.join(BASE_DIR, '../data/project.csv')
    WORKERS_FILE = os.path.join(BASE_DIR, '../data/workers.csv')
    EQUIPMENT_FILE = os.path.join(BASE_DIR, '../data/equipment.csv')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploads')
    ACTIVITY_CODES_FILE = os.path.join(BASE_DIR, '../data/activity_codes.csv')
    MATERIALS_FILE = os.path.join(BASE_DIR, '../data/materials.csv')
    PICTURES_FILE = os.path.join(BASE_DIR, '../data/pictures.csv')
    DAILY_PICTURES_FILE = os.path.join(BASE_DIR, '../database/daily_pictures.csv')
    DOCUMENTS_FILE = os.path.join(BASE_DIR, '../database/documents.csv')
    SUBCONTRACTORS_FILE = os.path.join(BASE_DIR, '../data/subcontractors.csv')
    DATA_FILE_PATH = os.path.join(BASE_DIR, '../data/daily_report_data.csv')

# ----------------------------------------
# Environment-Specific Configs
# ----------------------------------------

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "../database/TCC.db")}'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fallback-dev-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///local-dev.db")
    DO_BUILD = os.getenv("SCM_DO_BUILD_DURING_DEPLOYMENT", "false").lower() == "true"
    SPEECH_API_KEY = os.getenv("SPEECH_API_KEY")
    SPEECH_REGION = os.getenv("SPEECH_REGION")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ----------------------------------------
# Optional: Config map for use in create_app()
# ----------------------------------------
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# Final check
logger.info(f"Config loaded. Using database: {Config.SQLALCHEMY_DATABASE_URI}")
