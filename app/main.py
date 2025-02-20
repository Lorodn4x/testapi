from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, models
from .core.config import settings

app = FastAPI(
    title="OpenAI-Compatible Pollinations.AI Proxy",
    description="A fully OpenAI-compatible API interface for Pollinations.AI with function calling support",
    version="1.0.0",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/v1")
app.include_router(models.router, prefix="/v1")

@app.get("/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 