from fastapi import FastAPI
from app.database import Base, engine   
from app.models import user


app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to IOWEYOU"}
