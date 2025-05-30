"""Tests for /data-entry/initialize-day"""

def test_initialize_day(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    resp = client.post(
        "/data-entry/initialize-day", json={"dateStamp": "2024-12-06"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "success"
    with client.session_transaction() as sess:
        assert sess["report_date"] == "2024-12-06"