from ...db.action_database import fetch_actions, delete_action, update_action_service
from ...db.supplier_database import fetch_supplier
from ...db.target_database import fetch_target
from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter()

# Define class for updating actions
class actual_vals(BaseModel):
    co2_red: float
    spend: float
    rev_unlocked: float

@router.get("/action")
def get_actions(user_id: str = Header()):
    return fetch_actions(user_id)

@router.delete("/action/{action_id}")
def del_actions(action_id: str, user_id: str = Header()):
    return delete_action(user_id, action_id)

@router.put("/action/{action_id}")
def update_action(action_id: str, userVals: actual_vals, user_id: str = Header()):
    return update_action_service(user_id, action_id, userVals.co2_red, userVals.spend, userVals.rev_unlocked)

@router.get("/supplier")
def get_supplier(user_id: str = Header()):
    return fetch_supplier(user_id)

@router.get("/target")
def get_target(user_id: str = Header()):
    return fetch_target(user_id)