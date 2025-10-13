import os
import resend
import logging
from sqlalchemy.orm import Session
from models.email import Email
from models.user import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Resend with API key from environment
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Debug logging
logger.info(f"🔑 RESEND_API_KEY present: {bool(resend.api_key)}")
logger.info(f"🔑 RESEND_API_KEY length: {len(resend.api_key) if resend.api_key else 0}")
if resend.api_key:
    logger.info(f"🔑 RESEND_API_KEY starts with: {resend.api_key[:7]}...")

# Initialize Resend with API key from environment
resend.api_key = os.getenv("RESEND_API_KEY", "")


class EmailProvider:
    """Base provider interface for future flexibility"""
    def send(self, from_email: str, to: str, subject: str, body: str):
        raise NotImplementedError


class ResendProvider(EmailProvider):
    """Resend email provider implementation"""
    
    def __init__(self):
        if not resend.api_key:
            raise ValueError("RESEND_API_KEY not set in environment variables")

   def send(self, from_email: str, to: str, subject: str, body: str):
    """Send email via Resend API"""
    try:
        params = {
            "from": from_email,
            "to": [to],
            "subject": subject,
            "html": body,
        }
        
        logger.info(f"📧 Attempting to send email:")
        logger.info(f"  From: {from_email}")
        logger.info(f"  To: {to}")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  API Key set: {bool(resend.api_key)}")
        
        email = resend.Emails.send(params)
        
        logger.info(f"✅ Resend response: {email}")
        
        return {
            "success": True,
            "email_id": email.get("id"),
            "status": "sent"
        }
    except Exception as e:
        logger.error(f"❌ Resend send failed: {str(e)}")
        raise RuntimeError(f"Resend send failed: {str(e)}")


def send_email_via_resend(
    db: Session, 
    sender: User, 
    recipient_email: str, 
    subject: str, 
    body: str
):
    """
    Send email via Resend and log to database
    
    Args:
        db: Database session
        sender: User object (from authentication)
        recipient_email: Recipient email address
        subject: Email subject
        body: Email body (HTML)
    
    Returns:
        Dictionary with email info and status
    """
    
    # Construct from email using verified domain
    # Option 1: Use your verified domain (after domain verification)
    from_email = f"{sender.email.split('@')[0]} <noreply@arktechnologies.ai>"
    
    # Option 2: Use Resend's test domain (for quick testing)
    # from_email = "onboarding@resend.dev"
    
    # Send via Resend
    provider = ResendProvider()
    result = provider.send(from_email, recipient_email, subject, body)
    
    # Save to database
    email_record = Email(
        sender_id=sender.id,
        recipient=recipient_email,
        subject=subject,
        body=body,
        is_sent=True,
        is_draft=False,
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)
    
    return {
        "message": "Email sent successfully",
        "email_id": email_record.id,
        "external_id": result.get("email_id"),
        "status": result.get("status")
    }


def get_user_inbox(db: Session, user_id: int, user_email: str, skip: int = 0, limit: int = 50):
    """
    Get emails received by user
    
    Args:
        db: Database session
        user_id: Current user's ID
        user_email: Current user's email
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of Email objects
    """
    return db.query(Email).filter(
        Email.recipient == user_email,
        Email.is_deleted == False
    ).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


def get_user_sent_emails(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get emails sent by user"""
    return db.query(Email).filter(
        Email.sender_id == user_id,
        Email.is_sent == True,
        Email.is_deleted == False
    ).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


def get_user_drafts(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get draft emails by user"""
    return db.query(Email).filter(
        Email.sender_id == user_id,
        Email.is_draft == True,
        Email.is_deleted == False
    ).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


def get_user_archived(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get archived emails by user"""
    return db.query(Email).filter(
        Email.sender_id == user_id,
        Email.is_archived == True,
        Email.is_deleted == False
    ).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


def get_user_trash(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get deleted emails by user"""
    return db.query(Email).filter(
        Email.sender_id == user_id,
        Email.is_deleted == True
    ).order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


def get_email_by_id(db: Session, email_id: int, user_id: int, user_email: str):
    """
    Get specific email if user has access
    
    Args:
        db: Database session
        email_id: Email ID to fetch
        user_id: Current user's ID
        user_email: Current user's email
    
    Returns:
        Email object or None
    """
    email = db.query(Email).filter(Email.id == email_id).first()
    
    # Check if user is sender or recipient
    if email and (email.sender_id == user_id or email.recipient == user_email):
        return email
    
    return None


def update_email(db: Session, email_id: int, user_id: int, update_data: dict):
    """Update email properties (archive, delete, etc.)"""
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.sender_id == user_id
    ).first()
    
    if email:
        for key, value in update_data.items():
            if hasattr(email, key):
                setattr(email, key, value)
        
        db.commit()
        db.refresh(email)
        return email
    
    return None


def delete_email_permanently(db: Session, email_id: int, user_id: int):
    """Permanently delete email from database"""
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.sender_id == user_id
    ).first()
    
    if email:
        db.delete(email)
        db.commit()
        return True
    
    return False