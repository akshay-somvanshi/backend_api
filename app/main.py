from fastapi import FastAPI
from pydantic import BaseModel
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.suggestions import router as suggestion_router

# Initialise app
app = FastAPI(title='Dash API', version='v1')

# Include dashboard router
app.include_router(router=dashboard_router)
# Include knowledge router
app.include_router(router=knowledge_router)
# Include suggestion router
app.include_router(router=suggestion_router)

@app.get("/health")
async def health():
    return {"message" : "The API is up and running!"}

@app.get("/")
async def home():
    return {"message" : "Welcome to Dash's backend API!"}