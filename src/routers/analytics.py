from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from utils.auth import get_current_active_user
from services.analytics_service import get_email_activity_summary

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/email-activity")
def get_email_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return get_email_activity_summary(db, current_user.id)
