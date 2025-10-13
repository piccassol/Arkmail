from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from schemas.user import UserCreate, Token
from utils.auth import create_access_token, get_password_hash, verify_password
import uuid

router = APIRouter(tags=["authentication"])

# Add this class for Google Auth
class GoogleAuthRequest(BaseModel):
    email: str
    name: str
    google_id: str

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Try to find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.hashedPassword:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password using bcrypt
    if not verify_password(form_data.password, user.hashedPassword):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
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
        name=user.username,
        hashedPassword=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"email": new_user.email, "name": new_user.name}

@router.post("/google-auth", response_model=Token)
async def google_auth(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate or register a user via Google OAuth
    Creates user if doesn't exist, returns JWT token
    """
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Create new user for Google OAuth
        hashed_password = get_password_hash(request.google_id)
        user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            name=request.name,
            hashedPassword=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}