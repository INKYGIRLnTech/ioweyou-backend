from fastapi import FastAPI
from app.database import Base, engine   
from app.models import user, loan


app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(loan.router, prefix="/loans", tags=["loan