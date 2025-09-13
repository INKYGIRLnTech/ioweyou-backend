from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.dependencies import get_db
from app.models.loan import Loan
from app.models.user import User
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse
from app import models, schemas


router = APIRouter(
    prefix="/loans",
    tags=["loans"],
)

# Create a new loan
@router.post("/", response_model=LoanResponse)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    lender = db.query(User).filter(User.id == loan.lender_id).first()
    borrower = db.query(User).filter(User.id == loan.borrower_id).first()

    if not lender or not borrower:
        raise HTTPException(status_code=400, detail="Lender or borrower are not found")
    
    db_loan = Loan(
        lender_id=loan.lender_id,
        borrower_id=loan.borrower_id,
        amount=loan.amount,
        interest_rate=loan.interest_rate,
        status=loan.status,
        due_date=loan.due_date,
        created_at=datetime.now(timezone.utc),  
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)

    return db_loan


# Get loan by ID
@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

# Update a loan status (approve/reject)
@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(loan_id: int, loan_update: LoanUpdate, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    for field, value in loan_update.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)

        loan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(loan)

    return loan

# List all loans
@router.get("/", response_model=list[LoanResponse])
def list_loans(
    lender_id: int | None = None,
    borrower_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Loan)

    if lender_id: 
        query = query.filter(Loan.lender_id == lender_id)
    if borrower_id:
        query = query.filter(Loan.borrower_id == borrower_id)

    return query.all()

# Delete a loan
@router.delete("/{loan_id}")
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    db.delete(loan)
    db.commit()
    return {"detail": f"Loan {loan_id} deleted successfully"}
