from fastapi import APIRouter, Header
from .dashboard import getActions, getSuppliers, getTargets

router = APIRouter()

## Routers for dashboard
@router.get("/action")
def get_actions(user_id: str = Header()):
    return getActions(user_id)

@router.get("/supplier")
def get_supplier(user_id: str = Header()):
    return getSuppliers(user_id)

@router.get("/target")
def get_target(user_id: str = Header()):
    return getTargets(user_id)

## Routers for knowledge page