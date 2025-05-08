#!/usr/bin/env python
import os
import logging
from dotenv import load_dotenv

# ────────────────────────────────────────────────────
# 1) Load .env immediately, before any imports that read getenv()
# ────────────────────────────────────────────────────
basedir    = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded environment from {dotenv_path}")
else:
    print(f"No .env found at {dotenv_path}; relying on system env")

# ────────────────────────────────────────────────────
# 2) Fallback for DATABASE_URL if missing
# ────────────────────────────────────────────────────
if not os.getenv("DATABASE_URL"):
    fallback = "sqlite:///database/TCC.db"
    os.environ["DATABASE_URL"] = fallback
    print(f"WARNING: DATABASE_URL not set, falling back to {fallback}")

# ────────────────────────────────────────────────────
# 3) Create the Flask app
# ────────────────────────────────────────────────────
from app import create_app
from app.config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Creating Flask app…")
app = create_app()
logger.info("Flask app created.")

env   = os.getenv("FLASK_ENV", "production")
debug = env == "development"

logger.info(f"Starting Flask in {env!r} mode (debug={debug})")
logger.info(f"Using DB URI: {Config.SQLALCHEMY_DATABASE_URI!r}")
logger.info("WEATHER_API_KEY present? %s", bool(os.getenv("WEATHER_API_KEY")))


# ────────────────────────────────────────────────────
# 4) Only start the built-in server if run.py is called directly
#    (Gunicorn will import `app` without ever hitting this block)
# ────────────────────────────────────────────────────
if __name__ == "__main__":
    # You can bind to 0.0.0.0 and pick up a PORT envvar if you like:
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port, debug=debug)
