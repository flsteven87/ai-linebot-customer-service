"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI LineBot Customer Service",
    description="API for AI-powered LINE customer service bot",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routers
from app.api.v1.health import router as health_router
from app.api.v1.linebot import router as linebot_router

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(linebot_router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Root endpoint returning API information.
    
    Returns:
        dict: Basic API information.
    """
    return {
        "name": "AI LineBot Customer Service API", 
        "version": "0.1.0",
        "status": "active"
    } 