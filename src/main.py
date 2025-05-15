"""
Main module for the Newsaroo API application.
"""

import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("newsaroo.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Newsaroo API",
    description="News summarization API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our router
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {"status": "healthy"} 