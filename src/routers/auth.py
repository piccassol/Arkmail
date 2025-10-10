from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, Token
from utils.auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Try to authenticate with username first, then with email
    user = authenticate_user(db, form_data.username, form_data.password)
    
    # If username fails, try email
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
        if user:
            from utils.auth import verify_password
            if not verify_password(form_data.password, user.hashed_password):
                user = None
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserCreate)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user