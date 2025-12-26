"""
Image storage service for managing temporary and permanent image storage.
"""
import os
import base64
import uuid
from typing import Optional
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMP_IMAGE_DIR = os.path.join(BASE_DIR, "images", "temp")
PERMANENT_IMAGE_DIR = os.path.join(BASE_DIR, "images", "permanent")


def _ensure_directories():
    """Ensure image directories exist."""
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
    os.makedirs(PERMANENT_IMAGE_DIR, exist_ok=True)


def save_temp_image(image_bytes: bytes, temp_id: str) -> str:
    """
    Save image to temporary storage.
    
    Args:
        image_bytes: PNG bytes with transparent background
        temp_id: Temporary ID
    
    Returns:
        Relative path to saved image
    """
    _ensure_directories()
    
    filename = f"{temp_id}.png"
    filepath = os.path.join(TEMP_IMAGE_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    
    relative_path = f"images/temp/{filename}"
    logger.info(f"Saved temporary image: {relative_path}")
    return relative_path


def save_permanent_image(image_bytes: bytes, item_id: str) -> str:
    """
    Save image to permanent storage.
    
    Args:
        image_bytes: PNG bytes with transparent background
        item_id: Inventory item ID
    
    Returns:
        Relative path to saved image
    """
    _ensure_directories()
    
    filename = f"{item_id}.png"
    filepath = os.path.join(PERMANENT_IMAGE_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    
    relative_path = f"images/permanent/{filename}"
    logger.info(f"Saved permanent image: {relative_path}")
    return relative_path


def move_temp_to_permanent(temp_id: str, item_id: str) -> Optional[str]:
    """
    Move image from temporary to permanent storage.
    
    Args:
        temp_id: Temporary ID
        item_id: Inventory item ID
    
    Returns:
        Relative path to permanent image or None if temp image not found
    """
    temp_path = os.path.join(TEMP_IMAGE_DIR, f"{temp_id}.png")
    permanent_path = os.path.join(PERMANENT_IMAGE_DIR, f"{item_id}.png")
    
    if not os.path.exists(temp_path):
        logger.warning(f"Temporary image not found: {temp_path}")
        return None
    
    # Move file
    os.rename(temp_path, permanent_path)
    
    relative_path = f"images/permanent/{item_id}.png"
    logger.info(f"Moved image from temp to permanent: {relative_path}")
    return relative_path


def delete_temp_image(temp_id: str) -> bool:
    """
    Delete temporary image.
    
    Args:
        temp_id: Temporary ID
    
    Returns:
        True if deleted, False if not found
    """
    filepath = os.path.join(TEMP_IMAGE_DIR, f"{temp_id}.png")
    
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Deleted temporary image: {filepath}")
        return True
    
    return False


def delete_permanent_image(item_id: str) -> bool:
    """
    Delete permanent image.
    
    Args:
        item_id: Inventory item ID
    
    Returns:
        True if deleted, False if not found
    """
    filepath = os.path.join(PERMANENT_IMAGE_DIR, f"{item_id}.png")
    
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Deleted permanent image: {filepath}")
        return True
    
    return False


def get_image_url(image_path: str, base_url: str = "") -> str:
    """
    Generate image URL from path.
    
    Args:
        image_path: Relative image path
        base_url: Base URL for API (e.g., "https://api.example.com")
    
    Returns:
        Full image URL
    """
    if base_url:
        return f"{base_url}/{image_path}"
    return image_path

