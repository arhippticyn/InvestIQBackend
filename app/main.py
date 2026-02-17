from fastapi import FastAPI
from app.routes.router import router

app = FastAPI()

app.include_router(router=router)

@app.get('/')
async def root():
    return 'ez'