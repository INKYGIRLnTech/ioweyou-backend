from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db
from tests.test_database import override_get_db, create_test_database

# Set up test DB and override FastAPI dependency
app.dependency_overrides = {}
app.dependency_overrides[get_db] = override_get_db

create_test_database()
client = TestClient(app)

def test_create_loan():
    response = client.post("/loans/", json={
        "amount": 1000.0,
        "interest_rate": 5.0,
        "end_date": "2023-12-31",
        "borrower_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 1000.0
    assert data["interest_rate"] == 5.0

def test_get_loans(): 
    response = client.get("/loans/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_loan_id():
    # You can first create a loan, then fetch by ID
    create_response = client.post("/loans/", json={
        "amount": 2000.0,
        "interest_rate": 4.5,
        "end_date": "2024-01-01",
        "borrower_id": 2
    })
    loan_id = create_response.json()["id"]

    response = client.get(f"/loans/{loan_id}")
    assert create_response.status_code == 200
    assert response.status_code == 200
    assert response.json()["id"] == loan_id   