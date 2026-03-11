from pydantic import BaseModel,EmailStr

class RegisterUser(BaseModel):
    email:EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    budget: float

    class Config:
        orm_mode = True
    