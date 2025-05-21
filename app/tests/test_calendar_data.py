# app/tests/test_calendar_data.py

import json
from app import create_app

def test_calendar_data():
    # Create the app and test client
    app = create_app()
    app.testing = True
    client = app.test_client()

    # Mock user session data to match expected result
    with client.session_transaction() as session:
        session['user_id'] = '101'
        session['daily_data'] = {
            "2025-03-01": {
                "projects": {
                    "25-101": {"status": "completed"}
                }
            },
            "2025-03-02": {
                "projects": {
                    "24-408": {"status": "in_progress"}
                }
            }
        }

    # Call the /calendar/calendar-data route
    response = client.get('/calendar/calendar-data')
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = json.loads(response.data)
    print("Response JSON:")
    print(json.dumps(data, indent=4))

    assert 'calendar' in data
    assert "2025-03-01" in data['calendar'], "Expected date not found in calendar data"
    assert "25-101" in data['calendar']["2025-03-01"]
