from .client_init import get_storage_bucket
from ..core.exceptions import StorageError
from datetime import timedelta
import uuid
from google import auth
from dotenv import load_dotenv
from fastapi import HTTPException, File

credentials, project = auth.default()
credentials.refresh(auth.transport.requests.Request())

# Get bucket
bucket = get_storage_bucket()

def fetch_documents(user_id: str):
    try:
        # All the documents for this user will be under this prefix
        prefix = f"users/{user_id}/uploads/"
        blobs = bucket.list_blobs(prefix=prefix)

        documents = []

        for blob in blobs:
            documents.append({
                "file_name": blob.name.split("/")[-1],
                "gcs_path": blob.name,
                "size_bytes": blob.size,
                "content_type": blob.content_type,
                "updated": blob.updated.isoformat()
            })

        return documents
    
    except Exception as e:
        raise StorageError("Failed to fetch document from Cloud storage", e)

def generate_signed_url(document_path, action, user_id):
    try:
        # Check the path can be accessed by user
        assert document_path.startswith(f"users/{user_id}/"), "Access denied"
        
        blob = bucket.blob(document_path)

        response_disposition = None
        if action == "download":
            response_disposition = f'attachment; filename="{blob.name.split("/")[-1]}"'

        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=5),
            method='GET', 
            service_account_email="441601669115-compute@developer.gserviceaccount.com",
            access_token=credentials.token,
            response_disposition=response_disposition
        )
        
        return url
    
    except Exception as e:
        raise StorageError("Failed to fetch signed url from Cloud storage", e)

def upload_document(user_id, file):
    # Create a unique path
    file_name = file.filename.split(".")[0]
    file_ext = file.filename.split(".")[-1]
    # document_id = str(uuid.uuid4())
    gcs_path = f"users/{user_id}/uploads/{file_name}.{file_ext}"

    try:
        output_blob = bucket.blob(gcs_path)

        output_blob.upload_from_file(
            file.file,
            content_type=file.content_type
        )

        return {
            "message": "Upload successful",
            # "document_id": document_id,
            "file_name": file.filename,
            "gcs_path": gcs_path
        }
    
    except Exception as e:
        return StorageError("Failed to upload document to Cloud storage", e)
        
