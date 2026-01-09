from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.suggestions import router as suggestion_router
from app.core.exceptions import DatabaseError, StorageError

# Initialise app
app = FastAPI(title='Dash API', version='v1')

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, err: DatabaseError):
    # Log error
    print(f"Database failure: {err.error}")

    return JSONResponse(
        status_code=500,
        content={"detail": "A database error has occurred."}
    )

@app.exception_handler(StorageError)
async def storage_exception_handler(request: Request, err: StorageError):
    # Log error
    print(f"Storage failure: {err.error}")

    return JSONResponse(
        status_code=500,
        content={"detail": "A cloud storage error has occurred."}
    )

# Include dashboard router
app.include_router(router=dashboard_router)
# Include knowledge router
app.include_router(router=knowledge_router)
# Include suggestion router
app.include_router(router=suggestion_router)

@app.get("/")
async def home():
    return {"message" : "Welcome to Dash's backend API!"}