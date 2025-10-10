from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "User" 

    id = Column(String, primary_key=True, index=True)  
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    emailVerified = Column(DateTime(timezone=True), nullable=True)
    image = Column(String, nullable=True)
    hashedPassword = Column(String, nullable=True) 
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now())
    
    # Keep your relationships
    sent_emails = relationship("Email", back_populates="sender", foreign_keys="Email.sender_id")
    owned_newsletters = relationship("Newsletter", back_populates="owner", foreign_keys="Newsletter.owner_id")