from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.routes import router as api_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Business Idea Scorer",
    description="AI-driven scoring system for business ideas and investment opportunities",
    version="0.1.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Business Idea Scorer API is running"}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
