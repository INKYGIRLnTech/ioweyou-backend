from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Loan, User

# SQLite in-memory database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create the database engine and session
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create the database tables
def create_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

# Dependency override for FastAPI
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()