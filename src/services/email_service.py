import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session
from src.models.email import Email
from src.models.user import User

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")


class EmailProvider:
    """Base provider interface for future flexibility (SES, Postmark, etc.)"""
    def send(self, to: str, subject: str, body: str):
        raise NotImplementedError


class SendGridProvider(EmailProvider):
    def __init__(self):
        if not SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY not set in environment variables")
        self.client = SendGridAPIClient(SENDGRID_API_KEY)

    def send(self, to: str, subject: str, body: str):
        message = Mail(
            from_email="no-reply@aurorarift.ai",  # customize domain with verified sender
            to_emails=to,
            subject=subject,
            html_content=body,
        )
        try:
            response = self.client.send(message)
            return response.status_code
        except Exception as e:
            raise RuntimeError(f"SendGrid send failed: {e}")


def send_email_from_db(db: Session, sender: User, recipient: str, subject: str, body: str):
    """Send and log an email from the database"""
    provider = SendGridProvider()
    status_code = provider.send(recipient, subject, body)

    email_record = Email(
        sender_id=sender.id,
        recipient=recipient,
        subject=subject,
        body=body,
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)

    return {
        "message": "Email sent successfully",
        "status_code": status_code,
        "email_id": email_record.id,
    }
