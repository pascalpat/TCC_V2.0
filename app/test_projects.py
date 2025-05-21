import pytest
from app import create_app, db
from app.models.core_models import Project

@pytest.fixture
def client():
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        # Seed a sample project
        project = Project(name='Sample Project', project_number='P1', category='Demo')
        db.session.add(project)
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_list_projects_returns_numbers(client):
    resp = client.get('/projects/list')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'project_numbers' in data
    assert isinstance(data['project_numbers'], list)
    assert data['project_numbers'][0]['project_number'] == 'P1'

def test_set_project_stores_session(client):
    resp = client.post('/projects/set_project', json={'projectNumber': 'P1'})
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess['project_number'] == 'P1'

def test_set_project_invalid_id(client):
    resp = client.post('/projects/set_project', json={'projectNumber': 'INVALID'})
    assert resp.status_code == 404
    data = resp.get_json()
    assert data.get('error') is not None
