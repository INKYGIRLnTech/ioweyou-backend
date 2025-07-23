from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, engine
from app import models, schemas
from datetime import datetime, timezone

# Make sure the tables are created
models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new loan
@router.post("/", response_model=schemas.LoanResponse)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    db_loan = models.Loan(
        amount=loan.amount,
        interest_rate=loan.interest_rate,
        start_date=datetime.now(timezone.utc),
        end_date=loan.end_date,
        borrower_id=loan.borrower_id
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

# Get all loans
@router.get("/", response_model=List[schemas.LoanResponse])
def get_loans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    loans = db.query(models.Loan).offset(skip).limit(limit).all()
    return loans

# Get a loan by ID
@router.get("/{loan_id}", response_model=schemas.LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan

# Update a loan
@router.put("/{loan_id}", response_model=schemas.LoanResponse)
def update_loan(loan_id: int, loan: schemas.LoanUpdate, db: Session = Depends(get_db)):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    for key, value in loan.dict(exclude_unset=True).items():
        setattr(db_loan, key, value)
    
    db.commit()
    db.refresh(db_loan)
    return db_loan

# Delete a loan
@router.delete("/{loan_id}", response_model=schemas.LoanResponse)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    db.delete(db_loan)
    db.commit()
    return db_loan