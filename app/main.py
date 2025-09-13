from fastapi import FastAPI
from app.database import Base, engine   
from app.routes.loans import router as loans_router
from app.routes.user import router as user_router
import email_validator


app = FastAPI()

app.include_router(loans_router)
app.include_router(user_router)

# Print all registered route paths for debugging
print("Registered routes:")
for r in app.routes:
    print(f"{r.path} - {r.name}")

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to IOWEYOU"}
