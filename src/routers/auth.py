from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, Token
from utils.auth import authenticate_user, create_access_token, get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for: {form_data.username}")
    
    # Try username first
    user = authenticate_user(db, form_data.username, form_data.password)
    
    # If username fails, try email
    if not user:
        logger.info(f"Username auth failed, trying email")
        user = db.query(User).filter(User.email == form_data.username).first()
        if user:
            if not verify_password(form_data.password, user.hashed_password):
                logger.warning(f"Password verification failed for email: {form_data.username}")
                user = None
            else:
                logger.info(f"Email auth successful for: {form_data.username}")
        else:
            logger.warning(f"No user found with email: {form_data.username}")
    else:
        logger.info(f"Username auth successful for: {form_data.username}")
    
    if not user:
        logger.error(f"Authentication failed for: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid email/username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserCreate)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {user.email}")
    return new_user