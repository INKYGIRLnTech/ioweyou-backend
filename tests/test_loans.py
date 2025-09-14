from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db
from tests.test_database import override_get_db, create_test_database


# Set up test DB and override FastAPI dependency
app.dependency_overrides = {}
app.dependency_overrides[get_db] = override_get_db

create_test_database()
client = TestClient(app)


def _create_users():
    # Create two users to act as lender and borrower
    r1 = client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com", "password": "pw1"},
    )
    assert r1.status_code == 200, r1.text
    r2 = client.post(
        "/users/",
        json={"username": "bob", "email": "bob@example.com", "password": "pw2"},
    )
    assert r2.status_code == 200, r2.text
    return r1.json()["id"], r2.json()["id"]


def test_loans_crud_flow():
    lender_id, borrower_id = _create_users()
    # login to get access token
    login = client.post("/auth/login", json={"email": "alice@example.com", "password": "pw1"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    # Create a loan as lender (alice)
    due_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    create_payload = {
        "lender_id": lender_id,
        "borrower_id": borrower_id,
        "amount": 1000.0,
        "interest_rate": 5.0,
        "status": "pending",
        "due_date": due_date,
    }
    create_resp = client.post("/loans/", json=create_payload, headers=auth)
    assert create_resp.status_code == 200, create_resp.text
    loan = create_resp.json()
    loan_id = loan["id"]
    assert loan["amount"] == 1000.0
    assert loan["interest_rate"] == 5.0
    assert loan["lender_id"] == lender_id
    assert loan["borrower_id"] == borrower_id

    # List loans
    list_resp = client.get("/loans/", headers=auth)
    assert list_resp.status_code == 200
    loans = list_resp.json()
    assert isinstance(loans, list)
    assert any(l["id"] == loan_id for l in loans)

    # Get loan by id
    get_resp = client.get(f"/loans/{loan_id}", headers=auth)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == loan_id

    # Update loan status
    update_resp = client.put(f"/loans/{loan_id}", json={"status": "approved"}, headers=auth)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "approved"

    # Delete loan
    delete_resp = client.delete(f"/loans/{loan_id}", headers=auth)
    assert delete_resp.status_code == 200
    assert "deleted successfully" in delete_resp.json()["detail"]

    # Verify deleted
    missing_resp = client.get(f"/loans/{loan_id}", headers=auth)
    assert missing_resp.status_code == 404

def test_forbidden_for_non_participant():
    # create three users
    a = client.post("/users/", json={"username": "alice2", "email": "alice2@example.com", "password": "pw"}).json()
    b = client.post("/users/", json={"username": "bob2", "email": "bob2@example.com", "password": "pw"}).json()
    c = client.post("/users/", json={"username": "charlie2", "email": "charlie2@example.com", "password": "pw"}).json()

    # alice2 login
    login_a = client.post("/auth/login", json={"email": "alice2@example.com", "password": "pw"})
    token_a = login_a.json()["access_token"]
    auth_a = {"Authorization": f"Bearer {token_a}"}
    # bob2 login
    login_b = client.post("/auth/login", json={"email": "bob2@example.com", "password": "pw"})
    token_b = login_b.json()["access_token"]
    auth_b = {"Authorization": f"Bearer {token_b}"}
    # create loan as alice2 (lender=alice2, borrower=bob2)
    due_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    loan = client.post(
        "/loans/",
        json={"lender_id": a["id"], "borrower_id": b["id"], "amount": 10, "interest_rate": 1.0, "due_date": due_date},
        headers=auth_a,
    ).json()
    loan_id = loan["id"]
    # charlie2 login and attempt access
    login_c = client.post("/auth/login", json={"email": "charlie2@example.com", "password": "pw"})
    token_c = login_c.json()["access_token"]
    auth_c = {"Authorization": f"Bearer {token_c}"}
    # forbidden get
    r = client.get(f"/loans/{loan_id}", headers=auth_c)
    assert r.status_code == 403
    # forbidden update
    r = client.put(f"/loans/{loan_id}", json={"status": "approved"}, headers=auth_c)
    assert r.status_code == 403
