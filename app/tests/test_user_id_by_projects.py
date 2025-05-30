"""Tests for the helper that loads user projects from CSV."""

import os
from tempfile import NamedTemporaryFile
import pandas as pd
from app.utils.user_id_by_projects import get_user_projects


def test_get_user_projects(app):
    with app.app_context():
        with NamedTemporaryFile('w+', suffix='.csv', delete=False) as tmp:
            pd.DataFrame([
                {"user_id": "101", "project": "P1"},
                {"user_id": "102", "project": "P2"},
            ]).to_csv(tmp.name, index=False)
            app.config["PROJECT_FILE"] = tmp.name
            result = get_user_projects("101")
        os.remove(tmp.name)

    assert isinstance(result, list)
    assert result[0]["project"] == "P1"