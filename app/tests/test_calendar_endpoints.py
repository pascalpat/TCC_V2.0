import json
from datetime import date
from app import db
from app.models.core_models import Project
from app.models.daily_report_status import DailyReportStatus


def create_sample_data():
    project_a = Project(name="Project A", project_number="24-401", category="Test")
    project_b = Project(name="Project B", project_number="24-404", category="Test")
    db.session.add_all([project_a, project_b])
    db.session.commit()

    entries = [
        DailyReportStatus(project_id=project_a.id, report_date=date(2025, 1, 6), report_status='completed'),
        DailyReportStatus(project_id=project_b.id, report_date=date(2025, 1, 6), report_status='in_progress'),
        DailyReportStatus(project_id=project_a.id, report_date=date(2025, 1, 7), report_status='in_progress'),
    ]
    db.session.add_all(entries)
    db.session.commit()
    return project_a, project_b


def test_calendar_page_authenticated(client):
    with client.session_transaction() as sess:
        sess['user_id'] = '123'
    response = client.get('/calendar/')
    assert response.status_code == 200
    assert b'calendar-grid' in response.data


def test_calendar_data_structure(client, app):
    with app.app_context():
        project_a, project_b = create_sample_data()

    with client.session_transaction() as sess:
        sess['user_id'] = '123'

    response = client.get('/calendar/calendar-data')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'calendar' in data
    assert 'projects' in data

    assert data['calendar']['2025-01-06'][project_a.project_number] == 'completed'
    assert data['calendar']['2025-01-06'][project_b.project_number] == 'in_progress'
    assert data['calendar']['2025-01-07'][project_a.project_number] == 'in_progress'

    assert data['projects'][str(project_a.id)].startswith(project_a.project_number)
    assert data['projects'][str(project_b.id)].startswith(project_b.project_number)
