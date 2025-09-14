import os
from sqlalchemy import create_engine, text
from app.security import get_password_hash


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)


def main():
    temp = get_password_hash("temp123")
    with engine.begin() as conn:
        # Only update rows where hashed_password is NULL
        conn.execute(text("UPDATE users SET hashed_password = :h WHERE hashed_password IS NULL"), {"h": temp})
    print("Backfill complete. Set a temporary password for NULL entries.")


if __name__ == "__main__":
    main()

