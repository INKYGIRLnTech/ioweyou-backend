from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LoanBase(BaseModel):
    amount: float = Field(..., description="The amount of the loan")
    interest_rate: float = Field(..., description="The interest as a percentage")
    status: Optional[str] = Field("pending", description="The status of the loan (e.g., pending, approved, rejected)")

class LoanCreate(LoanBase):
    lender_id: int = Field(..., description="ID of the lender")
    borrower_id: int = Field(..., description="ID of the borrower")

class LoanUpdate(BaseModel):
    amount: Optional[float] = Field(None, description="The amount of the loan")
    interest_rate: Optional[float] = Field(None, description="The interest as a percentage")
    status: Optional[str] = Field(None, description="The status of the loan (e.g., pending, approved, rejected)")
    #due_date: Optional[datetime] = Field(None, description="Due date for the loan repayment") to be added later

class LoanResponse(BaseModel):
    id: int 
    lender_id: int 
    borrower_id: int
    due_date: Optional[datetime] 
    created_at: datetime 
    updated_at: datetime
    is_active: bool 

    class Config:
        from_attributes = True
        