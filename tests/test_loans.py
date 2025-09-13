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

    # Create a loan
    due_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    create_payload = {
        "lender_id": lender_id,
        "borrower_id": borrower_id,
        "amount": 1000.0,
        "interest_rate": 5.0,
        "status": "pending",
        "due_date": due_date,
    }
    create_resp = client.post("/loans/", json=create_payload)
    assert create_resp.status_code == 200, create_resp.text
    loan = create_resp.json()
    loan_id = loan["id"]
    assert loan["amount"] == 1000.0
    assert loan["interest_rate"] == 5.0
    assert loan["lender_id"] == lender_id
    assert loan["borrower_id"] == borrower_id

    # List loans
    list_resp = client.get("/loans/")
    assert list_resp.status_code == 200
    loans = list_resp.json()
    assert isinstance(loans, list)
    assert any(l["id"] == loan_id for l in loans)

    # Get loan by id
    get_resp = client.get(f"/loans/{loan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == loan_id

    # Update loan status
    update_resp = client.put(f"/loans/{loan_id}", json={"status": "approved"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "approved"

    # Delete loan
    delete_resp = client.delete(f"/loans/{loan_id}")
    assert delete_resp.status_code == 200
    assert "deleted successfully" in delete_resp.json()["detail"]

    # Verify deleted
    missing_resp = client.get(f"/loans/{loan_id}")
    assert missing_resp.status_code == 404
