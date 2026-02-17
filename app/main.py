from fastapi import FastAPI
from app.routes.router import router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import SECRET_KEY

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://localhost:5174'
]


app.include_router(router=router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

@app.get('/')
async def root():
    return 'ez'