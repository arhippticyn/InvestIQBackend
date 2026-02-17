import jwt

def encode_token(payload, SECRET_KEY, algorithm):
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=algorithm)