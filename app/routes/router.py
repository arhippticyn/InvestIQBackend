from fastapi import APIRouter
from .auth.auth import router as auth_router
from .profile.profile import router as profile_router
from .finances.finances import router as finances_router

router = APIRouter()

router.include_router(
    router=auth_router,
    prefix='/auth',
    tags=['Auth']
)

router.include_router(
    router=profile_router,
    prefix='/profile',
    tags=['Profile']
)

router.include_router(
    router=finances_router,
    prefix='/finances',
    tags=['Finances']
)