from fastapi import APIRouter, Depends, HTTPException, status, Response, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from app.schemas.user import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.db.sessions import get_db
from app.core.config import ALGORITM, SECRET_KEY, AUTH_EXP
from app.services.auth import encode_token, verify_token
from app.schemas.user import RegisterUser, UserResponse, LoginUser
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from urllib.parse import urlencode
from app.services.auth import get_currunt_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

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
async def login(res: Response, user_data: LoginUser = Body(...), db: AsyncSession = Depends(get_db)):
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


@router.get('/google')
async def google_login(request: Request):
    redirect_uri = 'http://127.0.0.1:8000/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback')
async def google_callback(request: Request,res: Response,db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token['userinfo']

    email = user_info['email']
    username = user_info['email'].split('@')[0]
    provider = 'google'
    provider_id = user_info['sub']

    user = (await db.execute(select(User).where(User.provider == provider, User.provider_id == provider_id))).scalars().first()

    if not user:
        user = User(username=username, email=email, hash_password=None, provider=provider, provider_id=provider_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }

    access_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algorithm=ALGORITM, type='access', exp=10)
    refresh_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algorithm=ALGORITM, type='refresh', exp=1440)

    res.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            max_age=60 * 10,
            samesite='lax',  
            secure=False,
            path='/'
        )

    res.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age = 60 * 60 * 24,
        samesite='lax',  
        secure=False,
        path='/'
    )

    params_access = urlencode({'access_token': access_token})
    params_refresh= urlencode({'refresh_token': refresh_token})


    return RedirectResponse(url=f'http://localhost:5174/?{params_access}&{params_refresh}')


@router.delete('/logout')
async def logout(res: Response):
    res.delete_cookie('access_token', path='/')
    res.delete_cookie('refresh_token', path='/')

    return {'detail': 'Log Out Success'}



