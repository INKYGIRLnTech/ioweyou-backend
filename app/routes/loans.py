from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, engine
from app.dependencies import get_db
from app import models, schemas
from datetime import datetime, timezone

# Make sure the tables are created
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Create a new loan
@router.post("", response_model=schemas.LoanResponse)
def create_loans(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        new_loan = models.Loan(**loan.dict())
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)

        print("DEBUG: Created Loan object ->", new_loan)

        return new_loan
    except Exception as e:
        db.rollback()
        print(f"Error creating loan: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Get all loans
@router.get("", response_model=List[schemas.LoanResponse])
def get_loans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    loans = db.query(models.Loan).offset(skip).limit(limit).all()
    return loans

# Get a loan by ID
@router.get("{loan_id}", response_model=schemas.LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan

# Update a loan
@router.put("{loan_id}", response_model=schemas.LoanResponse)
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
@router.delete("{loan_id}", response_model=schemas.LoanResponse)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    db.delete(db_loan)
    db.commit()
    return db_loan