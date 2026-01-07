from ...db.action_database import fetch_actions
from ...db.supplier_database import fetch_supplier
from ...db.target_database import fetch_target

def getActions(user_id):
    return fetch_actions(user_id)

def getSuppliers(user_id):
    return fetch_supplier(user_id)

def getTargets(user_id):
    return fetch_target(user_id)