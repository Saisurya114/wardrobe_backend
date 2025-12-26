"""
SQLAlchemy models for inventory persistence.
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'inventory', 'inventory.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class InventoryItem(Base):
    """
    Canonical InventoryItem model for permanent storage.
    """
    __tablename__ = "inventory_items"
    
    # Primary key
    id = Column(String, primary_key=True)  # Format: topwear_shirt_01
    
    # Image storage
    image_path = Column(String, nullable=False)  # Relative path: images/permanent/{id}.png
    image_url = Column(String, nullable=True)  # For future cloud storage
    
    # Classification
    category = Column(String, nullable=False)  # topwear, bottomwear, footwear, accessories
    type = Column(String, nullable=False)  # shirt, tshirt, pants, shorts, shoes
    subtype = Column(String, default="unknown")
    
    # Color information (stored as JSON)
    color_name = Column(String, nullable=False)
    color_rgb = Column(JSON, nullable=False)  # [r, g, b]
    color_group = Column(String, nullable=False)  # blue, red, white, black, neutral
    
    # Additional metadata
    fit = Column(String, default="unknown")
    formality = Column(String, default="unknown")
    season = Column(JSON, default=[])  # Array of strings
    
    # Confidence scores (optional)
    type_confidence = Column(Float, nullable=True)
    color_confidence = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON response."""
        return {
            "id": self.id,
            "image_path": self.image_path,
            "image_url": self.image_url,
            "category": self.category,
            "type": self.type,
            "subtype": self.subtype,
            "color": {
                "name": self.color_name,
                "rgb": self.color_rgb,
                "group": self.color_group
            },
            "fit": self.fit,
            "formality": self.formality,
            "season": self.season,
            "type_confidence": self.type_confidence,
            "color_confidence": self.color_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


def init_db():
    """Initialize database and create tables."""
    os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

