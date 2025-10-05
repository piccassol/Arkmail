from sqlalchemy.orm import Session
from src.models.email import Email
from src.models.user import User

def create_email(db: Session, sender_id: int, recipient_ids: list, subject: str, body: str):
    db_email = Email(
        subject=subject,
        body=body,
        sender_id=sender_id,
        is_sent=False
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def send_email_from_db(db: Session, email_id: int):
    # Implement actual email sending logic here
    email = db.query(Email).filter(Email.id == email_id).first()
    if email:
        email.is_sent = True
        db.commit()
    return email
