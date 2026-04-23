from ...db.document_storage import fetch_documents, up_document, generate_signed_url, del_document
from ...db.apiConnection_database import add_api_connection
from fastapi import APIRouter, Header, File, UploadFile, Query
from pydantic import BaseModel

router = APIRouter()

class add_api(BaseModel):
    provider: str
    account_number: str
    api_key: str

@router.get("/document")
def get_document(user_id: str = Header()):
    return fetch_documents(user_id)

@router.post("/document")
def upload_file(user_id: str = Header(), file: UploadFile = File()):
    return up_document(user_id, file)

@router.get("/document/{document_path:path}/url")
def get_document_url(document_path: str, action: str = Query("view"), user_id: str = Header()):
    return generate_signed_url(document_path, action, user_id)

@router.delete("/document/{document_path:path}")
def delete_document(document_path: str, user_id: str = Header()):
    return del_document(user_id, document_path)

@router.post("/add-api")
def add_api(api_data: add_api, user_id: str = Header()):
    return add_api_connection(user_id, api_data.provider, api_data.account_number, api_data.api_key)