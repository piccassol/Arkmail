from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, Token
from utils.auth import create_access_token, get_password_hash, verify_password
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for: {form_data.username}")
    
    # Try to find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.hashedPassword:
        logger.warning(f"User not found or no password: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(form_data.password, user.hashedPassword):
        logger.warning(f"Password verification failed for: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    logger.info(f"Login successful for: {form_data.username}")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with UUID
    hashed_password = get_password_hash(user.password)
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.username,  # Map username to name
        hashedPassword=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {user.email}")
    return {"email": new_user.email, "name": new_user.name}