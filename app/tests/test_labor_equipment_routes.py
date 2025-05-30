from app import db
from app.models.core_models import Project, ActivityCode


def setup_project_and_activity(app):
    with app.app_context():
        project = Project(name="LE Proj", project_number="LE1", category="Test")
        activity = ActivityCode(code="AC1", description="desc")
        db.session.add(project)
        db.session.add(activity)
        db.session.commit()
        return project, activity


def test_confirm_and_fetch_labor_equipment(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    project, activity = setup_project_and_activity(app)
    payload = {
        "project_id": project.project_number,
        "date_of_report": "2025-03-04",
        "usage": [
            {
                "employee_id": None,
                "equipment_id": None,
                "hours": 8,
                "activity_code_id": activity.id,
                "payment_item_id": None,
                "cwp_id": None,
                "is_manual": True,
                "manual_name": "John",
                "manual_type": "worker",
            }
        ],
    }
    resp = client.post("/labor-equipment/confirm-labor-equipment", json=payload)
    assert resp.status_code == 200
    ids = resp.get_json()["records"]
    assert len(ids) == 1

    resp = client.get(
        "/labor-equipment/by-project-date",
        query_string={"project_id": project.project_number, "date": "2025-03-04"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["workers"]) == 1