from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.db.sessions import get_db
from app.core.config import ALGORITM, SECRET_KEY, AUTH_EXP
from app.services.auth import encode_token
from app.schemas.user import RegisterUser, UserResponse, LoginUser
from passlib.context import CryptContext

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain:str, hash:str):
    return pwd_context.verify(plain,hash)


@router.post('/register', response_model=UserResponse)
async def register(user: RegisterUser, res: Response, db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.email == user.email))).scalars().first()

    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is already register')
    
    user_db = User(username=user.username, email=user.email, hash_password=hash_password(user.password), provider='local', provider_id=user.username)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    payload = {
        'id': user_db.id,
        'username': user_db.username,
        'email': user_db.email,
    }

    access = encode_token(payload, SECRET_KEY, ALGORITM, type='access', exp=10)
    refresh = encode_token(payload, SECRET_KEY, ALGORITM, type='refresh', exp=1440)

    res.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            max_age=60 * 10,
            samesite='lax',  
            secure=False,
            path='/'
        )

    res.set_cookie(
        key='refresh_token',
        value=refresh,
        httponly=True,
        max_age = 60 * 60 * 24,
        samesite='lax',  
        secure=False,
        path='/'
    )

    return user_db


@router.post('/login', response_model=UserResponse)
async def login(res: Response, user_data: LoginUser, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == user_data.email))).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is not found')
    
    if not verify_password(user_data.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username or password is not correct')
    
    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }

    access = encode_token(payload, SECRET_KEY, ALGORITM, type='access', exp=10)
    refresh = encode_token(payload, SECRET_KEY, ALGORITM, type='refresh', exp=1440)

    res.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            max_age=60 * 10,
            samesite='lax',  
            secure=False,
            path='/'
        )

    res.set_cookie(
        key='refresh_token',
        value=refresh,
        httponly=True,
        max_age = 60 * 60 * 24,
        samesite='lax',  
        secure=False,
        path='/'
    )

    return user
