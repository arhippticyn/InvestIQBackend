from fastapi import FastAPI
from app.routes.router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:5173'
]


app.include_router(router=router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return 'ez'