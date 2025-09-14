from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.dependencies import get_db, get_current_user
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
def create_loan(loan: LoanCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Only allow lender to be the authenticated user unless admin
    if user.role != 'admin' and loan.lender_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to create loan for another lender")
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
def get_loan(loan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if user.role != 'admin' and user.id not in (loan.lender_id, loan.borrower_id):
        raise HTTPException(status_code=403, detail="Not allowed to view this loan")
    return loan

# Update a loan status (approve/reject)
@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(loan_id: int, loan_update: LoanUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if user.role != 'admin' and user.id not in (loan.lender_id, loan.borrower_id):
        raise HTTPException(status_code=403, detail="Not allowed to update this loan")
    
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
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Non-admins only see their own loans
    query = db.query(Loan)
    if user.role != 'admin':
        query = query.filter((Loan.lender_id == user.id) | (Loan.borrower_id == user.id))

    if lender_id: 
        query = query.filter(Loan.lender_id == lender_id)
    if borrower_id:
        query = query.filter(Loan.borrower_id == borrower_id)

    return query.all()

# Delete a loan
@router.delete("/{loan_id}")
def delete_loan(loan_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if user.role != 'admin' and user.id not in (loan.lender_id, loan.borrower_id):
        raise HTTPException(status_code=403, detail="Not allowed to delete this loan")
    
    db.delete(loan)
    db.commit()
    return {"detail": f"Loan {loan_id} deleted successfully"}
