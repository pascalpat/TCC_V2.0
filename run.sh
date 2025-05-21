#!/usr/bin/env bash
# ------------------------
# Codex “Run command” fallback
# ------------------------
# after the install script finishes, Codex will auto-run this

# ensure the right FLASK_APP is set
export FLASK_APP=run.py
export FLASK_ENV=development

# start the server on all interfaces
flask run --host=0.0.0.0
