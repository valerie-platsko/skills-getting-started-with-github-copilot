import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # ensure each test starts with a clean participant list
    for a in activities.values():
        a["participants"] = []
    yield


def test_get_activities_empty():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # all activities should initially have empty participant lists
    for _, details in data.items():
        assert "participants" in details
        assert details["participants"] == []


def test_signup_and_duplicate():
    activity = "Soccer Team"
    email = "alice@example.com"

    # successful signup
    r = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # participant should be present
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]

    # duplicate signup should return 400
    r3 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert r3.status_code == 400


def test_unregister_success():
    activity = "Mathletes"
    email = "bob@example.com"

    # sign up first
    r = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert r.status_code == 200

    # unregister
    r2 = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert r2.status_code == 200
    assert "Unregistered" in r2.json().get("message", "")

    # verify removed
    r3 = client.get("/activities")
    assert email not in r3.json()[activity]["participants"]


def test_unregister_not_signed_up():
    activity = "Science Club"
    email = "charlie@example.com"

    r = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert r.status_code == 400


def test_unregister_activity_not_found():
    r = client.delete(f"/activities/{quote('Nonexistent')}/participants", params={"email": 'x@y.com'})
    assert r.status_code == 404
