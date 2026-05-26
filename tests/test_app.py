import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activities():
    # Arrange is handled by the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    email = "teststudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_participant_removes_participant():
    # Arrange
    email = "unregister@mergington.edu"
    signup_response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
