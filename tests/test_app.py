import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

# preserve original state for reset
_original_activities = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Clear and restore activities before each test (AAA arrange)."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))
    yield


def test_root_redirect():
    # Arrange: fixture has reset state
    # Act (don't follow the redirect so we can see the 307)
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities_returns_dict():
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_signup_success_adds_participant():
    # Arrange
    email = "new@mergington.edu"
    # Act
    resp = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    # Act
    resp = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "")


def test_signup_nonexistent_activity_404():
    # Act
    resp = client.post(
        "/activities/Nonexistent/signup", params={"email": "foo@bar"}
    )
    # Assert
    assert resp.status_code == 404


def test_unregister_success_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    # Act
    resp = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_nonparticipant_returns_404():
    # Arrange
    email = "ghost@mergington.edu"
    # Act
    resp = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 404


def test_unregister_nonexistent_activity_404():
    # Act
    resp = client.delete(
        "/activities/NoSuch/signup", params={"email": "a@b"}
    )
    # Assert
    assert resp.status_code == 404
