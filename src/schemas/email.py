from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    body: str

class EmailCreate(EmailBase):
    recipient_ids: List[int]

class EmailResponse(EmailBase):
    id: int
    sender_id: int
    is_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ Fixed for Pydantic V2
