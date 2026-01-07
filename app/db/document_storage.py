from .client_init import get_storage_client
import os 
from dotenv import load_dotenv

# Load environment variable
load_dotenv()
bucket_id = os.getenv('BUCKET_ID')

def fetch_document(user_id):
    # Get storage client
    client = get_storage_client()

    document_bucket = client.get_bucket(bucket_id)
    users = document_bucket.list_blobs()

    for user in users:
        url = user.name
        parts = url.split("/")

        # The string is structured as users/user_id/uploads/file.pdf
        url_user_id = parts[1]

        # Only get documents for this user_id
        if url_user_id != user_id:
            continue

        
