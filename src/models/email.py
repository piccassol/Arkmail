from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    recipient = Column(String(255), nullable=False)
    
    # Foreign key to existing users table
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status flags
    is_sent = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to User model
    sender = relationship("User", back_populates="sent_emails")
    
    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject}', recipient='{self.recipient}')>"
