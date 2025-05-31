# Total Cost Control (TCC)

This repository contains a modular Flask and JavaScript application for tracking construction costs.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   The list includes `python-dotenv` so the app can load variables from a `.env`
   file during development.
2. Provide the following environment variables (see `.env.txt` for examples):
   - `DATABASE_URL` – SQLAlchemy connection string (defaults to `sqlite:///database/TCC.db` if unset).
   - `FLASK_SECRET_KEY` – secret key for sessions.
   - Optional: `WEATHER_API_KEY`, `SPEECH_API_KEY`, `SPEECH_REGION`.
   When `FLASK_ENV=development`, variables from a local `.env` file are loaded automatically by `run.py`.
3. Alembic migrations use `render_as_batch=True` when the database is SQLite. This is configured automatically in `migrations/env.py`.

4. Initialize the database:
   ```bash
   flask db upgrade
   ```
5. Create an initial user:
   ```bash
   python manage.py create-user
   ```
   The command will prompt for an email, name, role, and password. The password is stored using a secure hash.

## Running the Application

Use the main entry point `run.py` to start the Flask development server:
```bash
python run.py
```
This creates the application with `create_app()` and serves it on `localhost:5000` by default.

## Documentation

Additional documentation can be found in the `docs/` directory, including API references and a project tree overview. Architecture notes are in `readme_files/TCC_V2.0_Architecture_Documentation.docx`.


## Contributing

Before committing any code changes, run the test suite:

```bash
pytest
```

You can also use the helper script `codex_test_loop.py` to repeatedly run the tests until they pass.

## Testing

Before running the test suite, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
pytest
```

The `codex_test_loop.py` script performs the same installation step automatically before running tests in a loop.

