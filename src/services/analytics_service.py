from sqlalchemy.orm import Session

def get_email_activity_summary(db: Session, user_id: int):
    return {
        "openRate": 0.0,
        "clickRate": 0.0,
        "bounceRate": 0.0,
        "unsubscribeRate": 0.0
    }
