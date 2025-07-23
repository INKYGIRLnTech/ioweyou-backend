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

class LoanResponse(LoanBase):
    id: int = Field(..., description="ID of the loan")
    lender_id: int = Field(..., description="ID of the lender")
    borrower_id: int = Field(..., description="ID of the borrower")
    created_at: datetime = Field(..., description="Timestamp when the loan was created")
    updated_at: datetime = Field(..., description="Timestamp when the loan was last updated")
    is_active: bool = Field(..., description="Indicates if the loan is currently active")

    class Config:
        orm_mode = True