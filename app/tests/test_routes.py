import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 302  # Accept redirect as correct
    assert '/login' in response.headers.get('Location', '')