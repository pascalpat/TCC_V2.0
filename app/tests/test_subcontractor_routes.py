import datetime
from app import db
from app.models.core_models import Project, ActivityCode
from app.models.subcontractor_models import Subcontractor
from app.models.SubcontractorEntry import SubcontractorEntry


def setup_project_and_sub(app):
    with app.app_context():
        project = Project(name="S Proj", project_number="SP1", category="Demo")
        activity = ActivityCode(code="AC1", description="desc")
        sub = Subcontractor(name="Sub1", project=project)
        db.session.add_all([project, activity, sub])
        db.session.commit()
        return project, activity, sub


def test_get_entries_all_and_filtered(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
    project, activity, sub = setup_project_and_sub(app)
    with app.app_context():
        report_date = datetime.date(2025, 3, 4)
        pending = SubcontractorEntry(
            project_id=project.id,
            subcontractor_id=sub.id,
            activity_code_id=activity.id,
            date=report_date,
            status='pending'
        )
        completed = SubcontractorEntry(
            project_id=project.id,
            subcontractor_id=sub.id,
            activity_code_id=activity.id,
            date=report_date,
            status='completed'
        )
        db.session.add_all([pending, completed])
        db.session.commit()

    resp = client.get('/subcontractors/by-project-date', query_string={
        'project_id': project.project_number,
        'date': '2025-03-04'
    })
    assert resp.status_code == 200
    entries = resp.get_json()['entries']
    assert len(entries) == 2

    resp = client.get('/subcontractors/by-project-date', query_string={
        'project_id': project.project_number,
        'date': '2025-03-04',
        'status': 'pending'
    })
    assert resp.status_code == 200
    entries = resp.get_json()['entries']
    assert len(entries) == 1
    assert entries[0]['id'] == pending.id

def test_confirm_entries_with_manual_name(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'manager'
    project, activity, _sub = setup_project_and_sub(app)
    payload = {
        "project_id": project.project_number,
        "date": "2025-03-04",
        "usage": [
            {
                "subcontractor_id": None,
                "manual_name": "ManualSub",
                "num_employees": 2,
                "hours": 5,
                "activity_code_id": activity.id,
            }
        ]
    }
    resp = client.post('/subcontractors/confirm-entries', json=payload)
    assert resp.status_code == 200
    ids = resp.get_json()['records']
    assert len(ids) == 1

    resp = client.get('/subcontractors/by-project-date', query_string={
        'project_id': project.project_number,
        'date': '2025-03-04'
    })
    assert resp.status_code == 200
    entries = resp.get_json()['entries']
    assert len(entries) == 1
    assert entries[0]['subcontractor_name'] == 'ManualSub'
    