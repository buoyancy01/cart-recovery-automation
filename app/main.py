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
# Ensure that app.models.Base has the necessary SQLAlchemy imports and definitions
# for this to work correctly.
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
    allow_origins=["*"],  # Be more specific in production, e.g., ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Consider restricting to specific methods like ["GET", "POST"]
    allow_headers=["*"],  # Consider restricting to specific headers
)

# Include routers
# Ensure these modules (webhook, whatsapp, analytics) exist in app/api/
# and expose a 'router' object (e.g., from fastapi import APIRouter; router = APIRouter())
app.include_router(webhook.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(whatsapp.router, prefix="/api/v1", tags=["whatsapp"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

@app.get("/")
async def root():
    # Corrected Indentation
    return {
        "message": "Abandoned Cart Recovery API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    # Corrected Indentation
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z" # Consider using a dynamic timestamp here
    }

# This block is for local development, Render will typically run your app
# using a uvicorn command specified in your Render.yaml or start command.
if __name__ == "__main__":
    import uvicorn
    # Use environment variable for port in production for services like Render
    # Default to 8000 for local development.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
