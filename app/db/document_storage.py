from .client_init import get_storage_bucket
import os 
import uuid
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, File

def fetch_documents(user_id: str):
    # Get bucket
    bucket = get_storage_bucket()

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

def generate_signed_url(document_path, action):
    # Get bucket
    bucket = get_storage_bucket()

def upload_document(user_id, file):
    # Get bucket
    bucket = get_storage_bucket()

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
        return HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
        
