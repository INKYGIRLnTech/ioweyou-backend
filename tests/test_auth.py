from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db
from tests.test_database import override_get_db, create_test_database


# Set up test DB and override FastAPI dependency
app.dependency_overrides = {}
app.dependency_overrides[get_db] = override_get_db

create_test_database()
client = TestClient(app)


def test_auth_login_success_and_failure():
    # Create a user
    create_resp = client.post(
        "/users/",
        json={"username": "eve", "email": "eve@example.com", "password": "secret"},
    )
    assert create_resp.status_code == 200, create_resp.text

    # Successful login (get tokens)
    login_ok = client.post("/auth/login", json={"email": "eve@example.com", "password": "secret"})
    assert login_ok.status_code == 200, login_ok.text
    body = login_ok.json()
    assert "access_token" in body and "refresh_token" in body

    # Failed login (bad password)
    login_bad = client.post("/auth/login", json={"email": "eve@example.com", "password": "wrong"})
    assert login_bad.status_code == 401

    # Refresh token
    refresh = client.post("/auth/refresh", headers={"Authorization": f"Bearer {body['refresh_token']}"})
    assert refresh.status_code == 200
    refreshed = refresh.json()
    assert "access_token" in refreshed
