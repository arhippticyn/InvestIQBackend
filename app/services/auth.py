import jwt
from fastapi import Request, HTTPException, status
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from app.core.config import SECRET_KEY, ALGORITM

def encode_token(payload: dict, SECRET_KEY: str, algorithm: str, type: str, exp: int):
    payload_copy = payload.copy()

    payload_copy['type'] = type
    payload_copy['exp'] = int((datetime.now(timezone.utc) + timedelta(minutes=exp)).timestamp())

    return jwt.encode(payload=payload_copy, key=SECRET_KEY, algorithm=algorithm)

def verify_token(token: str):
     try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITM])
        return payload
     except PyJWTError:
        return None
        

def verify_user(req: Request):
    token = req.cookies.get('access_token')

    if token:
        payload = verify_token(token)
        if payload:
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

