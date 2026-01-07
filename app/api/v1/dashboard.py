from ...db.action_database import fetch_actions

def getActions(user_id):
    act = fetch_actions(user_id)
    print(act)
    return fetch_actions(user_id)