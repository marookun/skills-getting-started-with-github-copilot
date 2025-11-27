from fastapi.testclient import TestClient
import pytest
import sys
from pathlib import Path

# Ensure workspace root is on sys.path so `src` package can be imported
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy backup of participants to restore after each test
    backup = {k: v.get("participants", []).copy() for k, v in activities.items()}
    yield
    for k, p in backup.items():
        activities[k]["participants"] = p.copy()

def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email not present
    assert email not in activities[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]
    body3 = resp3.json()
    assert "Unregistered" in body3.get("message", "")

    # Unregister non-existent should return 404
    resp4 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp4.status_code == 404
