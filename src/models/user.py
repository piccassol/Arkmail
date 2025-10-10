from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(String, primary_key=True, index=True)  
    name = Column(String)  
    email = Column(String, unique=True, index=True)
   
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sent_emails = relationship("Email", back_populates="sender")
    owned_newsletters = relationship("Newsletter", back_populates="owner")