from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.newsletter import NewsletterCreate, NewsletterResponse
from models.user import User
from services.newsletter_service import send_newsletter
from utils.auth import get_current_user

router = APIRouter(
    prefix="/newsletters",
    tags=["newsletters"]
)


@router.post("/send", response_model=NewsletterResponse)
def send_newsletter_route(
    newsletter: NewsletterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a newsletter using Mailchimp and log it in the database.
    """
    try:
        result = send_newsletter(
            db=db,
            owner_id=current_user.id,
            title=newsletter.title,
            content=newsletter.content,
        )
        return NewsletterResponse(
            id=result["newsletter_id"],
            title=newsletter.title,
            content=newsletter.content,
            owner_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
