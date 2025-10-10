from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from schemas.email import EmailCreate, EmailResponse, EmailUpdate
from models.email import Email
from database import get_db
from models.user import User
from utils.auth import get_current_active_user
from services.email_service import (
    send_email_via_resend,
    get_user_inbox,
    get_user_sent_emails,
    get_user_drafts,
    get_user_archived,
    get_user_trash,
    get_email_by_id,
    update_email,
    delete_email_permanently
)

router = APIRouter()


@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def send_email(
    email: EmailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a new email via Resend
    
    Requires authentication. Sends email to recipient and saves to database.
    """
    try:
        result = send_email_via_resend(
            db=db,
            sender=current_user,
            recipient_email=email.recipient,
            subject=email.subject,
            body=email.body
        )
        
        # Fetch the created email record
        email_record = db.query(Email).filter(
            Email.id == result["email_id"]
        ).first()
        
        if not email_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email sent but failed to retrieve record"
            )
        
        return email_record
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/inbox", response_model=List[EmailResponse])
async def get_inbox(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's inbox (received emails)
    
    Returns emails where current user is the recipient.
    """
    emails = get_user_inbox(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        skip=skip,
        limit=limit
    )
    return emails


@router.get("/sent", response_model=List[EmailResponse])
async def get_sent(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's sent emails
    
    Returns emails sent by current user.
    """
    emails = get_user_sent_emails(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return emails


@router.get("/drafts", response_model=List[EmailResponse])
async def get_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's draft emails"""
    emails = get_user_drafts(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return emails


@router.get("/archived", response_model=List[EmailResponse])
async def get_archived(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's archived emails"""
    emails = get_user_archived(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return emails


@router.get("/trash", response_model=List[EmailResponse])
async def get_trash(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's deleted emails (trash)"""
    emails = get_user_trash(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return emails


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific email by ID
    
    User must be either sender or recipient to access.
    """
    email = get_email_by_id(
        db=db,
        email_id=email_id,
        user_id=current_user.id,
        user_email=current_user.email
    )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or you don't have access"
        )
    
    return email


@router.patch("/{email_id}", response_model=EmailResponse)
async def update_email_endpoint(
    email_id: int,
    email_update: EmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update email properties (archive, delete, etc.)
    
    Only the sender can update their emails.
    """
    update_data = email_update.dict(exclude_unset=True)
    
    email = update_email(
        db=db,
        email_id=email_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or you don't have permission to update it"
        )
    
    return email


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Permanently delete an email
    
    Only the sender can permanently delete their emails.
    """
    success = delete_email_permanently(
        db=db,
        email_id=email_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found or you don't have permission to delete it"
        )
    
    return None


# Convenience endpoints for common actions

@router.post("/{email_id}/archive", response_model=EmailResponse)
async def archive_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Archive an email"""
    email = update_email(
        db=db,
        email_id=email_id,
        user_id=current_user.id,
        update_data={"is_archived": True}
    )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email


@router.post("/{email_id}/trash", response_model=EmailResponse)
async def move_to_trash(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Move email to trash"""
    email = update_email(
        db=db,
        email_id=email_id,
        user_id=current_user.id,
        update_data={"is_deleted": True}
    )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email


@router.post("/{email_id}/restore", response_model=EmailResponse)
async def restore_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Restore email from trash"""
    email = update_email(
        db=db,
        email_id=email_id,
        user_id=current_user.id,
        update_data={"is_deleted": False, "is_archived": False}
    )
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email