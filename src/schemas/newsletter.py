from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsletterBase(BaseModel):
    name: str
    description: Optional[str] = None

class NewsletterCreate(NewsletterBase):
    pass

class NewsletterResponse(NewsletterBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
