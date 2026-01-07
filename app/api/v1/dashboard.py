from ...db.action_database import fetch_actions
from ...db.supplier_database import fetch_supplier
from ...db.target_database import fetch_target
from fastapi import APIRouter, Header

router = APIRouter()

@router.get("/action")
def get_actions(user_id: str = Header()):
    return fetch_actions(user_id)

@router.get("/supplier")
def get_supplier(user_id: str = Header()):
    return fetch_supplier(user_id)

@router.get("/target")
def get_target(user_id: str = Header()):
    return fetch_target(user_id)