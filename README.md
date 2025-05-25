# Total Cost Control (TCC)

This repository contains a modular Flask and JavaScript application for tracking construction costs.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide the following environment variables (see `.env.txt` for examples):
   - `DATABASE_URL` – SQLAlchemy connection string (defaults to `sqlite:///database/TCC.db` if unset).
   - `FLASK_SECRET_KEY` – secret key for sessions.
   - Optional: `WEATHER_API_KEY`, `SPEECH_API_KEY`, `SPEECH_REGION`.
   When `FLASK_ENV=development`, variables from a local `.env` file are loaded automatically by `run.py`.
3. Alembic migrations use `render_as_batch=True` when the database is SQLite. This is configured automatically in `migrations/env.py`.

## Running the Application

Use the main entry point `run.py` to start the Flask development server:
```bash
python run.py
```
This creates the application with `create_app()` and serves it on `localhost:5000` by default.

## Documentation

Additional documentation can be found in the `docs/` directory, including API references and a project tree overview. Architecture notes are in `readme_files/TCC_V2.0_Architecture_Documentation.docx`.
