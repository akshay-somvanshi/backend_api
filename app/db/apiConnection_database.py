from .client_init import get_firestore, get_secret_manager_client
from ..core.exceptions import DatabaseError
from dotenv import load_dotenv
import os
from pydantic import BaseModel

# Load the environment variables
load_dotenv()

class Api(BaseModel):
    provider: str
    account_number: str
    api_key: str

firestore = get_firestore()
secret_manager = get_secret_manager_client()
project_id = os.getenv('GOOGLE_PROJECT_ID')

def add_api_connection(user_id: str, provider: str, account_number: str, api_key: str):
    try:
        user_ref = firestore.collection("users").document(user_id)
        secret_manager_key = f"{user_id}_{provider}_key"

        user_ref.update({
            f"{provider}_account_num": account_number,
            f"{provider}_secret_name": secret_manager_key
        })

        parent = f"projects/{project_id}"

        secret = secret_manager.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_manager_key,
                "secret": {"replication": {"automatic": {}}},
            }
        )

        secret_data = api_key.encode("UTF-8")

        secret_manager.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": secret_data},
            }
        )
        
        return{
            "message": "API connection added successfully",
            "provider": provider,
            "account_number": account_number
        }
    except Exception as e:
        raise DatabaseError("Failed to add API connection", e)