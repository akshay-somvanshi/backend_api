from ...db.document_storage import fetch_documents, up_document, generate_signed_url
from fastapi import APIRouter, Header, File, UploadFile, Query

router = APIRouter()

@router.get("/document")
def get_document(user_id: str = Header()):
    return fetch_documents(user_id)

@router.post("/document")
def upload_file(user_id: str = Header(), file: UploadFile = File()):
    return up_document(user_id, file)

@router.get("/document/{document_path}/url")
def get_document_url(document_path: str, action: str = Query("view"), user_id: str = Header()):
    return generate_signed_url(document_path, action, user_id)