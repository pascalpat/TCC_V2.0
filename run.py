#!/usr/bin/env python
import os
from dotenv import load_dotenv

# ────────────────────────────────────────────────────
# 1) Load .env immediately, before any imports that read getenv()
# ────────────────────────────────────────────────────
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded environment from {dotenv_path}")
else:
    print(f"No .env found at {dotenv_path}; relying on system env")

# ────────────────────────────────────────────────────
import logging
from app import create_app
from app.config import Config
# ────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# 2) Fallback for DATABASE_URL if missing
if not os.getenv("DATABASE_URL"):
    fallback = "sqlite:///database/TCC.db"
    os.environ["DATABASE_URL"] = fallback
    logger.warning(f"DATABASE_URL not set, falling back to {fallback}")

logger.info("Creating Flask app...")
app = create_app()
logger.info("Flask app created.")

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    debug = (env == "development")
    logger.info(f"Starting Flask in {env!r} mode (debug={debug})")
    logger.info(f"Using DB URI: {Config.SQLALCHEMY_DATABASE_URI!r}")
    # Log whether the weather key was picked up
    logger.info("WEATHER_API_KEY present? %s", bool(os.getenv("WEATHER_API_KEY")))

    app.run(debug=debug)
