import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM",
            "max_participants": 10,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activities = app_module.activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Robotics Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Robotics Club"}
    assert email in app_module.activities["Robotics Club"]["participants"]


def test_signup_rejects_duplicate_without_changing_participants(client):
    # Arrange
    email = "student@example.com"
    expected_participants = [email]

    # Act
    response = client.post("/activities/Robotics Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert app_module.activities["Robotics Club"]["participants"] == expected_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Robotics Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Robotics Club"}
    assert email not in app_module.activities["Robotics Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Unknown Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_missing_participant(client):
    # Arrange
    email = "missing-student@example.com"

    # Act
    response = client.delete("/activities/Robotics Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
