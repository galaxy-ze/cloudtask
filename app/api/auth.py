from fastapi import APIRouter, Depends,status, HTTPException
from requests import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserRegistry, UserResponse, UserLogin
from app.models.user import User
from app.core.security import hash_password, verify_password


router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
def register(user_data: UserRegistry, db: Session = Depends(get_db)):
    email = str(user_data.email).lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=email,
        password_hash = hash_password(user_data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    db.refresh(user)

    return user


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    email = str(login_data.email).lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild email or password"
        )

    return{
        "message": "Login sucessful"
    }
