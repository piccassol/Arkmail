from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from .models.newsletter import Newsletter, NewsletterIssue
from .schemas.newsletter import NewsletterCreate, NewsletterIssueCreate
from .utils.auth import get_current_active_user
from .services.newsletter_service import create_newsletter, create_newsletter_issue, send_newsletter_issue
from .models.user import User

router = APIRouter(
    prefix="/newsletters",
    tags=["newsletters"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=Newsletter)
def create_new_newsletter(
    newsletter: NewsletterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_newsletter(
        db=db,
        name=newsletter.name,
        owner_id=current_user.id,
        description=newsletter.description
    )

@router.post("/{newsletter_id}/issues", response_model=NewsletterIssue)
def create_new_issue(
    newsletter_id: int,
    issue: NewsletterIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    if newsletter.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return create_newsletter_issue(db=db, newsletter_id=newsletter_id, subject=issue.subject, content=issue.content)

@router.post("/{newsletter_id}/issues/{issue_id}/send")
async def send_issue(
    newsletter_id: int,
    issue_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    background_tasks.add_task(send_newsletter_issue, db=db, issue_id=issue_id)
    return {"message": "Newsletter issue is being sent"}
