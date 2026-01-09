from .client_init import get_firestore
from ..core.exceptions import DatabaseError
from datetime import datetime

# Connect to firestore
firestore = get_firestore()

# Get now timestamp
now = datetime.utcnow()

def getSuggestions(user_id, chip_type):
    try:
        suggestions = (
            firestore.collection("suggestions")
            .where("user_id", "==", user_id)
            .where("type", "==", chip_type)
            # .where("expires_at", ">", now)
            .limit(4)
            .get()
        )

        return [suggestion.to_dict() for suggestion in suggestions]
    
    except Exception as e:
        raise DatabaseError("Failed to fetch suggestion from Firestore", e)
    