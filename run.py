#!/usr/bin/env python
import os
import logging
from dotenv import load_dotenv
from app import create_app
from app.config import Config

# ────────────────────────────────────────────────────
# 1) Load .env immediately, before any imports that read getenv()
# ────────────────────────────────────────────────────
basedir    = os.path.abspath(os.path.dirname(__file__))
dotenv_fp  = os.path.join(basedir, '.env')
if os.path.exists(dotenv_fp):
    load_dotenv(dotenv_fp)
    print(f"Loaded environment from {dotenv_fp}")
else:
    print(f"No .env found at {dotenv_fp}; relying on system env")

# ────────────────────────────────────────────────────
# 2) Ensure DATABASE_URL fallback
# ────────────────────────────────────────────────────
if not os.getenv("DATABASE_URL"):
    fallback = "sqlite:///database/TCC.db"
    os.environ["DATABASE_URL"] = fallback
    logging.warning(f"DATABASE_URL not set, falling back to {fallback}")

# ────────────────────────────────────────────────────
# 3) Create the app
# ────────────────────────────────────────────────────
logging.info("Creating Flask app…")
app = create_app()
logging.info("Flask app created.")

# Log some config details
env   = os.getenv("FLASK_ENV", "production")
debug = env == "development"
logging.info(f"Starting Flask in {env!r} mode (debug={debug})")
logging.info(f"Using DB URI: {Config.SQLALCHEMY_DATABASE_URI!r}")
logging.info("WEATHER_API_KEY present? %s", bool(os.getenv("WEATHER_API_KEY")))

# ────────────────────────────────────────────────────
# 4) Only run the dev server when executed directly.
#    Gunicorn (or any other WSGI server) will import `app`
#    without hitting this block.
# ────────────────────────────────────────────────────
if __name__ == '__main__':
    # Use host/port from env if set (Azure typically provides PORT)
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
