import os

# Force tests to run against the local SQLite test database instead of any production URL from .env
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
