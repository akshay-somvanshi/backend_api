from ...db.document_storage import fetch_documents, upload_document, generate_signed_url
from fastapi import APIRouter, Header, File, UploadFile

router = APIRouter()

@router.get("/document")
def get_document(user_id: str = Header()):
    return fetch_documents(user_id)

@router.post("/upload")
def upload_file(user_id: str = Header(), file: UploadFile = File()):
    return upload_document(user_id, file)

@router.get("/document/signed_url")
def get_document_url(document_path: str, action: str, user_id: str):
    return generate_signed_url(document_path, action, user_id)