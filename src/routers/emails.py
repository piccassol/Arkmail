from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import your schemas (singular: email)
from src.schemas.email import EmailCreate, EmailResponse

# Import your database models (singular: email)
from src.models.email import Email

# Import database session
from src.database import get_db

# Import user model and authentication dependencies
from src.models.user import User
from src.dependencies.auth import get_current_active_user

# Import your CRUD functions
from src.crud.email import create_email, send_email_from_db

router = APIRouter()

@router.post("/", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def send_email(
    email: EmailCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_email = create_email(db, current_user.id, email.recipient_ids, email.subject, email.body)
    background_tasks.add_task(send_email_from_db, db, db_email.id)
    return db_email