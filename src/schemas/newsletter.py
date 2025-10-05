from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsletterBase(BaseModel):
    title: str  # Changed from 'name'
    content: Optional[str] = None  # Changed from 'description'

class NewsletterCreate(NewsletterBase):
    pass

class NewsletterResponse(NewsletterBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ Fixed for Pydantic V2
