from ...db.suggestion_database import getSuggestions
from fastapi import APIRouter, Header

router = APIRouter()

@router.get("/suggestions")
def get_suggestions(user_id: str = Header(), chip_type: str = Header()):
    return getSuggestions(user_id, chip_type)