import pytest

def test_add_project_and_duplicate(client):
    project_data = {"name": "Proj1", "project_number": "P100", "category": "Demo"}

    resp1 = client.post('/projects/add', json=project_data)
    assert resp1.status_code == 201
    data1 = resp1.get_json()
    assert data1.get('id') is not None

    resp2 = client.post('/projects/add', json=project_data)
    assert resp2.status_code == 400
    data2 = resp2.get_json()
    assert 'already exists' in data2.get('error', '').lower()
