from fastapi import APIRouter, Header
from .dashboard import getActions

router = APIRouter()

@router.get("/action")
def get_actions(user_id: str = Header()):
    return getActions(user_id)