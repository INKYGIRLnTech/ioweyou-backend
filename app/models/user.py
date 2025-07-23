from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    loans_given = relationship("LoanGiven", back_populates="lender", foreign_keys="Loan.lender_id")
    loans_taken = relationship("LoanTaken", back_populates="borrower", foreign_keys="Loan.borrower_id")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"