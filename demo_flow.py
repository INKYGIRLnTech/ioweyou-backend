from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db


TEST_DB_URL = "sqlite:///./tmp_demo.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_demo():
    # Reset schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Override deps
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    print("== Register two users ==")
    u1 = client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com", "password": "pw1"},
    )
    u2 = client.post(
        "/users/",
        json={"username": "bob", "email": "bob@example.com", "password": "pw2"},
    )
    print("alice:", u1.status_code, u1.json())
    print("bob:", u2.status_code, u2.json())

    alice_id = u1.json()["id"]
    bob_id = u2.json()["id"]

    print("\n== Create loans between them ==")
    due = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    l1 = client.post(
        "/loans/",
        json={
            "lender_id": alice_id,
            "borrower_id": bob_id,
            "amount": 1500.0,
            "interest_rate": 3.5,
            "status": "pending",
            "due_date": due,
        },
    )
    l2 = client.post(
        "/loans/",
        json={
            "lender_id": bob_id,
            "borrower_id": alice_id,
            "amount": 500.0,
            "interest_rate": 2.0,
            "status": "pending",
            "due_date": due,
        },
    )
    print("loan1:", l1.status_code, l1.json())
    print("loan2:", l2.status_code, l2.json())

    loan1_id = l1.json()["id"]

    print("\n== List loans ==")
    lst = client.get("/loans/")
    print(lst.status_code, lst.json())

    print("\n== Fetch loan details ==")
    g = client.get(f"/loans/{loan1_id}")
    print(g.status_code, g.json())

    print("\n== Update a loan ==")
    upd = client.put(f"/loans/{loan1_id}", json={"status": "approved"})
    print(upd.status_code, upd.json())


if __name__ == "__main__":
    run_demo()

