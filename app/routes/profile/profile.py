from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import get_currunt_user
from app.schemas.user import UserResponse
from app.db.sessions import get_db
from sqlalchemy import select

router = APIRouter()

@router.get('/me', response_model=UserResponse)
async def get_user(user: User = Depends(get_currunt_user)):
    return user

@router.patch('/setusername', response_model=UserResponse)
async def set_username(new_username: str, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.id == user.id))).scalars().first()

    if new_username:
        user_db.username = new_username
        await db.commit()
        await db.refresh(user_db)

    return user_db

@router.patch('/budget')
async def patch_budget(new_budget: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    if new_budget:
        user.budget = new_budget
        await db.commit()

    return user.budget

@router.get('/budget')
async def get_budget(user: User = Depends(get_currunt_user)):
    return user.budget