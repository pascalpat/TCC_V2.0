import os
import re
import logging
from dotenv import load_dotenv

# ─── Setup ─────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()  # pull in any .env settings

# Base directory for this file: C:/Projects/TCC_V2.0/config.py’s folder
BASE_DIR       = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT   = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# ─── Database Path ─────────────────────────────────────────────────────────────

# Point directly at the sqlite file inside your project root
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'TCC.db')

def normalize_db_url(url: str) -> str:
    """Convert a plain path or already-valid URL into a SQLAlchemy DB URI."""
    known_schemes = (
        'sqlite://',
        'postgresql://',
        'mysql://',
        'oracle://',
        'mssql://',
    )
    lower = url.lower()
    if any(lower.startswith(s) for s in known_schemes):
        return url

    # If it looks like Windows C:\ or a relative path, make it an absolute path
    if re.match(r"^[a-zA-Z]:[\\/].*", url):
        abs_path = url
    else:
        abs_path = os.path.abspath(url)

    logger.warning(
        "DATABASE_URL '%s' missing scheme. Using sqlite path %s", url, abs_path
    )
    return f"sqlite:///{abs_path}"

# ─── Required Env Vars ─────────────────────────────────────────────────────────

def validate_config():
    required_env_vars = ['FLASK_SECRET_KEY', 'DATABASE_URL']
    optional_api_keys = ['WEATHER_API_KEY', 'SPEECH_API_KEY', 'SPEECH_REGION']
    env = os.getenv("FLASK_ENV", "production")



    for var in required_env_vars:
        if not os.getenv(var):
            if env == "production":
                raise RuntimeError(f"Critical Error: {var} is not set in Production!")
            logger.warning(f"Environment variable '{var}' is not set. Using default values.")
    for key in optional_api_keys:
        if not os.getenv(key):
            if env == "production":
                raise RuntimeError(f"Critical Error: {key} is not set in Production!")
            logger.warning(f"Environment variable '{key}' is not set. Some features may be disabled.")
validate_config()

# ─── Base Config ────────────────────────────────────────────────────────────────

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    SPEECH_API_KEY  = os.getenv('SPEECH_API_KEY')
    SPEECH_REGION   = os.getenv('SPEECH_REGION')

    # Use a full DATABASE_URL if provided, otherwise fall back to our sqlite file
    raw_db = os.getenv('DATABASE_URL', DEFAULT_DB_PATH)
    SQLALCHEMY_DATABASE_URI = normalize_db_url(raw_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE      = 'filesystem'
    SESSION_PERMANENT = False

    # Paths to your CSV/data files
    PROJECT_FILE        = os.path.join(BASE_DIR,  'data',     'project.csv')
    WORKERS_FILE        = os.path.join(BASE_DIR,  'data',     'workers.csv')
    EQUIPMENT_FILE      = os.path.join(BASE_DIR,  'data',     'equipment.csv')
    ACTIVITY_CODES_FILE = os.path.join(BASE_DIR,  'data',     'activity_codes.csv')
    MATERIALS_FILE      = os.path.join(BASE_DIR,  'data',     'materials.csv')
    SUBCONTRACTORS_FILE = os.path.join(BASE_DIR,  'data',     'subcontractors.csv')
    UPLOAD_FOLDER       = os.path.join(BASE_DIR,  'uploads')
    DATA_FILE_PATH      = os.path.join(BASE_DIR,  'data',     'daily_report_data.csv')
    # etc...

# ─── Environment-specific Configs ───────────────────────────────────────────────

class DevelopmentConfig(Config):
    DEBUG = True
    # In dev we explicitly re-use our sqlite file with the proper scheme
    SQLALCHEMY_DATABASE_URI = normalize_db_url(DEFAULT_DB_PATH)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", Config.SECRET_KEY)
    raw_db = os.getenv("DATABASE_URL", DEFAULT_DB_PATH)
    SQLALCHEMY_DATABASE_URI = normalize_db_url(raw_db)
    DO_BUILD          = os.getenv("SCM_DO_BUILD_DURING_DEPLOYMENT", "false").lower() == "true"
    SPEECH_API_KEY    = os.getenv("SPEECH_API_KEY")
    SPEECH_REGION     = os.getenv("SPEECH_REGION")
    WEATHER_API_KEY   = os.getenv("WEATHER_API_KEY")


config_map = {
    "development": DevelopmentConfig,
    "testing":    TestingConfig,
    "production": ProductionConfig,
}

# ─── Startup Logging ───────────────────────────────────────────────────────────

logger.info(f"Config loaded. Using database: {Config.SQLALCHEMY_DATABASE_URI}")
db_uri  = Config.SQLALCHEMY_DATABASE_URI
db_path = db_uri.replace('sqlite:///', '')
exists  = os.path.exists(db_path)
logger.info(f"→ SQLALCHEMY_DATABASE_URI = {db_uri}")
logger.info(f"→ underlying file {db_path!r} exists? {exists}")
