
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhook, whatsapp, analytics
from app.database import engine
from app.models import Base
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Create database tables
Base.metadata.create_all(bind=engine)
# Initialize FastAPI app
app = FastAPI(
title="Abandoned Cart Recovery API",
description="WhatsApp-based abandoned cart recovery automation",
version="1.0.0"
)
# Add CORS middleware
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)
# Include routers
app.include_router(webhook.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(whatsapp.router, prefix="/api/v1", tags=["whatsapp"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
@app.get("/")
async def root():
return {
"message": "Abandoned Cart Recovery API",
"version": "1.0.0",
"status": "running"
}
@app.get("/health")
async def health_check():
return {
"status": "healthy",
"timestamp": "2024-01-01T00:00:00Z"
}
if __name__ == "__main__":
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)


