from pydantic import BaseModel, EmailStr

class UserRegistry(BaseModel):
    email: EmailStr
    passwords: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr