from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.db.sessions import get_db
from app.core.config import ALGORITM, SECRET_KEY, AUTH_EXP
from app.services.auth import encode_token
from app.schemas.user import RegisterUser, UserResponse
from passlib.context import CryptContext

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')



def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain:str, hash:str):
    return pwd_context.verify(plain,hash)



@router.post('/register', response_model=UserResponse)
async def register(user: RegisterUser, db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.username == user.username))).scalars().first()

    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is already register')
    
    if not user_db:
        user_db = User(username=user.username, email=user.email, hash_password=hash_password(user.password), provider='local', provider_id=user.username)
        db.add(user_db)
        await db.commit()
        await db.refresh(user_db)

    return user_db


@router.post('/login')
async def login(form_data:OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == form_data.username))).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is not found')
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User is not found')
    
    if not verify_password(form_data.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username or password is not correct')
    
    payload = {
        'sub': user.username,
        'exp': AUTH_EXP
    }

    access_token = encode_token(payload, SECRET_KEY, ALGORITM)

    return {'access_token': access_token, 'type': 'bearer'}
        