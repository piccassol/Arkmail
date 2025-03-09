from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.newsletter import NewsletterCreate, NewsletterResponse
from ..services.newsletter_service import create_newsletter, send_newsletter
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/newsletters",
    tags=["newsletters"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=NewsletterResponse)
def create_new_newsletter(
    newsletter: NewsletterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_newsletter(db, newsletter.name, current_user.id, newsletter.description)

@router.post("/{newsletter_id}/send")
async def send_newsletter_issue(
    newsletter_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    background_tasks.add_task(send_newsletter, db, newsletter_id)
    return {"message": "Newsletter is being sent"}
