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
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DEBUG, FRONTEND_URL, FRONTEND_URL_DEPLOY
from urllib.parse import urlencode
from app.services.auth import get_currunt_user
from app.services.cookies import set_auth_cookies

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
    

    user_username = user.email.split('@')[0]
    user_db = User(username=user_username, email=user.email, hash_password=hash_password(user.password), provider='local', provider_id=user_username, budget=0)
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

    set_auth_cookies(res, access, refresh)

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

    set_auth_cookies(res, access, refresh)

    return user


@router.get('/google')
async def google_login(request: Request):
    redirect_uri = None
    
    if DEBUG:
        redirect_uri = 'http://localhost:8000/auth/google/callback'
    else:
        redirect_uri = 'https://investiq-nl1r.onrender.com/auth/google/callback'

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback')
async def google_callback(request: Request,db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token['userinfo']

    email = user_info['email']
    username = user_info['email'].split('@')[0]
    provider = 'google'
    provider_id = user_info['sub']

    user_local_provider = (await db.execute(select(User).where(User.provider == 'local', User.email == email))).scalars().first()

    if user_local_provider:
        return RedirectResponse(url=FRONTEND_URL)

    user = (await db.execute(select(User).where(User.provider == provider, User.provider_id == provider_id))).scalars().first()

    if not user:
        user = User(username=username, email=email, hash_password=None, provider=provider, provider_id=provider_id, budget=0)
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

    if DEBUG:
        redirect = RedirectResponse(url=f'{FRONTEND_URL}/home')
    else:
        redirect = RedirectResponse(url=f'{FRONTEND_URL_DEPLOY}/home')

    set_auth_cookies(redirect, access_token, refresh_token)

    return redirect


@router.delete('/logout')
async def logout(res: Response):
    res.delete_cookie('access_token', path='/')
    res.delete_cookie('refresh_token', path='/')

    return {'detail': 'Log Out Success'}


@router.get('/refresh')
async def get_access(request: Request, res: Response):
    token_refresh = request.cookies.get('refresh_token')

    if not token_refresh:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = verify_token(token_refresh)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    access_token = encode_token(payload, SECRET_KEY, algorithm=ALGORITM, type='access', exp=10)

    set_auth_cookies(res, access_token, token_refresh)

    return {"message": 'Success'}