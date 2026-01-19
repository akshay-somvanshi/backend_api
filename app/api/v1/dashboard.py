from ...db.action_database import fetch_actions, delete_action, update_action_service, get_unlocking_actions, get_dependent_on_actions
from ...db.supplier_database import fetch_supplier, get_supplier_targets_service
from ...db.target_database import fetch_target
from fastapi import APIRouter, Header
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Define class for updating actions
class actual_vals(BaseModel):
    co2_red: float
    spend: float
    rev_unlocked: float
    day_start: datetime
    day_end: datetime

@router.get("/action")
def get_actions(user_id: str = Header()):
    return fetch_actions(user_id)

@router.delete("/action/{action_id}")
def del_actions(action_id: str, user_id: str = Header()):
    return delete_action(user_id, action_id)

@router.put("/action/{action_id}")
def update_action(action_id: str, userVals: actual_vals, user_id: str = Header()):
    return update_action_service(user_id, action_id, userVals.co2_red, userVals.spend, userVals.rev_unlocked, userVals.day_start, userVals.day_end)

@router.get("/action/{action_id}/dependencies")
def get_dep_action(action_id: str, user_id: str = Header()):
    return get_dependent_on_actions(user_id, action_id)

@router.get("/action/{action_id}/unlocks")
def get_unlock_action(action_id: str, user_id: str = Header()):
    return get_unlocking_actions(user_id, action_id)

@router.get("/supplier")
def get_supplier(user_id: str = Header()):
    return fetch_supplier(user_id)

@router.get("/supplier/{supplier_id}/targets")
def get_supplier_targets(supplier_id: str, user_id: str = Header()):
    return get_supplier_targets_service(user_id, supplier_id)

@router.get("/target")
def get_target(user_id: str = Header()):
    return fetch_target(user_id)