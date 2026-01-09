from .client_init import get_firestore
from datetime import datetime

# Connect to firestore
firestore = get_firestore()

def getSuggestions(user_id, chip_type):
    # Get now timestamp
    now = datetime.utcnow()

    suggestions = (
        firestore.collection("suggestions")
        .where("user_id", "==", user_id)
        .where("type", "==", chip_type)
        # .where("expires_at", ">", now)
        .limit(4)
        .get()
    )

    return [suggestion.to_dict() for suggestion in suggestions]