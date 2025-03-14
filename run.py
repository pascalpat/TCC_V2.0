import os
import logging
from dotenv import load_dotenv  # Add this line
from app import create_app
from app.config import Config  # Correctly import the configuration class

logger = logging.getLogger(__name__)


# Load environment variables
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///database/TCC.db"
    logger.warning("DATABASE_URL not found in environment, using default: sqlite:///database/TCC.db")

logger.info("Creating Flask app...")
app = create_app()
logger.info("Flask app created.")

if __name__ == '__main__':
    # Get the Flask environment mode
    app_env = os.getenv("FLASK_ENV", "development")
    debug_mode = app_env == "development"

    logger.info(f"Starting Flask app in {app_env} mode")
    logger.info(f"Database URL: {Config.SQLALCHEMY_DATABASE_URI}")  # Logs the database being used

    # Run Flask application
    app.run(debug=debug_mode)