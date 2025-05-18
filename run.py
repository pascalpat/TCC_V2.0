#!/usr/bin/env python
import os
import logging
from app import create_app
from app.config import Config

# ────────────────────────────────────────────────────
# Configure logging ASAP
# ────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────
# 1) Load .env in development only
# ────────────────────────────────────────────────────
FLASK_ENV = os.getenv("FLASK_ENV", "production")
if FLASK_ENV == "development":
    # local .env only if present
    from dotenv import load_dotenv
    basedir    = os.path.abspath(os.path.dirname(__file__))
    dotenv_path = os.path.join(basedir, ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logger.info(f"Loaded local .env from {dotenv_path}")
    else:
        logger.warning(f"No local .env found at {dotenv_path}; relying on system env")

# ────────────────────────────────────────────────────
# 2) Ensure DATABASE_URL is set
# ────────────────────────────────────────────────────
if not os.getenv("DATABASE_URL"):
    fallback_db = "sqlite:///database/TCC.db"
    os.environ["DATABASE_URL"] = fallback_db
    logger.warning(f"DATABASE_URL not set; falling back to {fallback_db}")

# ────────────────────────────────────────────────────
# 3) Ensure FLASK_SECRET_KEY
# ────────────────────────────────────────────────────
if not os.getenv("FLASK_SECRET_KEY"):
    # only for local/dev
    fallback_secret = "dev-secret-key-change-me"
    os.environ["FLASK_SECRET_KEY"] = fallback_secret
    logger.warning("FLASK_SECRET_KEY not set; using fallback development key")

# ────────────────────────────────────────────────────
# 4) Create the Flask app
# ────────────────────────────────────────────────────
logger.info("Creating Flask app...")
app = create_app()
logger.info("Flask app created.")

# ────────────────────────────────────────────────────
# 5) If run directly, start the dev server
# ────────────────────────────────────────────────────
if __name__ == "__main__":
    debug = (FLASK_ENV == "development")
    # Show which keys we actually found
    logger.info(f"Environment: FLASK_ENV={FLASK_ENV!r}; debug={debug}")
    logger.info(f"DATABASE_URL      loaded? {bool(os.getenv('DATABASE_URL'))}")
    logger.info(f"FLASK_SECRET_KEY  loaded? {bool(os.getenv('FLASK_SECRET_KEY'))}")
    logger.info(f"WEATHER_API_KEY   loaded? {bool(os.getenv('WEATHER_API_KEY'))}")
    logger.info(f"SPEECH_API_KEY    loaded? {bool(os.getenv('SPEECH_API_KEY'))}")
    logger.info(f"SPEECH_REGION     loaded? {bool(os.getenv('SPEECH_REGION'))}")

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug)
