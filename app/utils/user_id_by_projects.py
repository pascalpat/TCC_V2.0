import pandas as pd
from flask import current_app
import os
from app.utils.data_loader import load_data

def get_user_projects(user_id):
    """
    Return projects for the given user, either via CSV or DB.
    If you're using CSV, we fetch the path from current_app.config.
    If you're using the DB, you can skip the CSV entirely.
    """

    # 1. If you still rely on CSV for user->projects logic:
    csv_path = current_app.config.get("PROJECT_FILE", "fallback_project.csv")
    abs_path = os.path.abspath(csv_path)

    # Check if file exists; if not, return empty or do something else
    if not os.path.exists(abs_path):
        current_app.logger.info(f"No project CSV found at {abs_path}, returning empty DataFrame.")
        return []  # or a default DataFrame, or however you want to handle missing files

    # 2. Load CSV with your load_data utility (if using CSV)
    df = load_data(abs_path)
    if df.empty:
        current_app.logger.info("Project CSV is empty or invalid, returning empty list.")
        return []

    # Possibly filter by user_id if your CSV has a user_id column:
    # user_projects = df[df['user_id'] == user_id]
    # return user_projects

    # For demonstration, just returning the entire CSV as a list of dicts:
    return df.to_dict(orient="records")


    # 3. If you're using the DB instead:
    #
    # projects = Project.query.filter_by(user_id=user_id).all()
    # return [
    #     {
    #         "id": p.id,
    #         "name": p.name,
    #         "project_number": p.project_number,
    #         "status": p.status,
    #         # etc.
    #     }
    #     for p in projects
    # ]