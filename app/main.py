from fastapi import FastAPI
from pydantic import BaseModel
# from .api.v1.router import router

# Initialise app
app = FastAPI(title='Dash API', version='v1')

# Include router
# app.include_router(router=router)

@app.get("/health")
async def health():
    return {"message" : "The API is up and running!"}

@app.get("/")
async def home():
    return {"message" : "Welcome to Dash's backend API!"}