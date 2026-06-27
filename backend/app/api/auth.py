from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(None)
) -> User:
    """Dependency to retrieve the logged-in user from the JWT cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Access token missing."
        )
        
    user_id = decode_access_token(access_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token invalid."
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user on the platform."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
        
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(response: Response, user_in: UserLogin, db: Session = Depends(get_db)):
    """Verifies credentials, generates JWT, and sets it in an HTTP-only Same-Site cookie."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
        
    # Generate token
    token = create_access_token(subject=user.id)
    
    # Set JWT in Same-Site HTTP-Only Cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        expires=60 * 60 * 24 * 7,
        samesite="lax",
        secure=False  # Set True in production (requires HTTPS)
    )
    
    return {
        "message": "Logged in successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    }

@router.post("/logout")
def logout(response: Response):
    """Logs out the user by clearing the access token cookie."""
    response.delete_cookie("access_token", samesite="lax")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the current authenticated user's profile."""
    return current_user
