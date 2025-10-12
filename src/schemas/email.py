from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmailBase(BaseModel):
    subject: str
    body: str


class EmailCreate(EmailBase):
    recipient: EmailStr
    is_draft: Optional[bool] = False


class EmailUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    is_archived: Optional[bool] = None
    is_deleted: Optional[bool] = None


class EmailResponse(EmailBase):
    id: int
    sender_id: str
    recipient: str
    is_sent: bool
    is_draft: bool
    is_archived: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    emails: list[EmailResponse]
    total: int
    page: int
    page_size: int
