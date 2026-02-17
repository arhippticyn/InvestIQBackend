from fastapi import APIRouter

router = APIRouter()

@router.get('/ez')
def ez():
    return 'ez'