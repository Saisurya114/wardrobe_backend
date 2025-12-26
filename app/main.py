from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.cloth import router as cloth_router
from app.api.inventory import router as inventory_router
from app.services.type_classifier import _load_model
from app.models import init_db
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Stylist Backend",
    description="Personal AI Stylist API for wardrobe digitization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Flutter app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(cloth_router, prefix="/api", tags=["cloth"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["inventory"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and preload models at startup."""
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Preload CLIP model
    try:
        logger.info("Preloading CLIP model...")
        _load_model()
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {str(e)}")
        # Continue anyway - will load on first request


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Stylist Backend is running"}
