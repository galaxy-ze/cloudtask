from fastapi import APIRouter
from app.schemas.user import UserRegistry, UserResponse

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserRegistry):
    return {
        "id": "1",
        "email": user.email,
    }