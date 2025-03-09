from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.email import EmailCreate, EmailResponse
from ..services.email_service import create_email, send_email_from_db
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=EmailResponse)
async def send_email(
    email: EmailCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_email = create_email(db, current_user.id, email.recipient_ids, email.subject, email.body)
    background_tasks.add_task(send_email_from_db, db, db_email.id)
    return db_email
