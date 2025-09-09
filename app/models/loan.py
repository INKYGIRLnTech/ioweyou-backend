from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    lender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    borrower_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0, nullable=False)
    status = Column(String, default='pending', nullable=False) # e.g., pending, approved, rejected
    #term_months = Column(Integer, nullable=False) to be added later
    due_date = Column(DateTime(timezone=True), nullable=True)  # Optional due date for the loan
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True)

    lender = relationship("User", foreign_keys=[lender_id], back_populates="loans_given")
    borrower = relationship("User", foreign_keys=[borrower_id], back_populates="loans_received")

    def __repr__(self):
        return f"<Loan(id={self.id}, amount={self.amount}, interest_rate={self.interest_rate})>"