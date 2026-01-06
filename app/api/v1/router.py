from fastapi import APIRouter
from dashboard import getActions

router = APIRouter()

@router.get("/action")
def out():
    return getActions()