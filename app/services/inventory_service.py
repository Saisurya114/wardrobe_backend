"""
Inventory service for managing permanent inventory in SQLite database.
"""
from sqlalchemy.orm import Session
from app.models import InventoryItem, get_db
from app.services.image_service import move_temp_to_permanent, delete_permanent_image
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def create_inventory_item(
    db: Session,
    item_id: str,
    image_path: str,
    category: str,
    item_type: str,
    color_name: str,
    color_rgb: list,
    color_group: str,
    subtype: str = "unknown",
    fit: str = "unknown",
    formality: str = "unknown",
    season: list = None,
    type_confidence: Optional[float] = None,
    color_confidence: Optional[float] = None,
    image_url: Optional[str] = None
) -> InventoryItem:
    """
    Create a new inventory item in the database.
    
    Args:
        db: Database session
        item_id: Inventory item ID
        image_path: Relative path to image
        category: Clothing category
        item_type: Clothing type
        color_name: Color name
        color_rgb: RGB array [r, g, b]
        color_group: Color group
        subtype: Subtype (default: "unknown")
        fit: Fit style (default: "unknown")
        formality: Formality level (default: "unknown")
        season: Season array (default: [])
        type_confidence: Type classification confidence
        color_confidence: Color detection confidence
        image_url: Full image URL (optional)
    
    Returns:
        Created InventoryItem
    """
    if season is None:
        season = []
    
    db_item = InventoryItem(
        id=item_id,
        image_path=image_path,
        image_url=image_url,
        category=category,
        type=item_type,
        subtype=subtype,
        color_name=color_name,
        color_rgb=color_rgb,
        color_group=color_group,
        fit=fit,
        formality=formality,
        season=season,
        type_confidence=type_confidence,
        color_confidence=color_confidence
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    logger.info(f"Created inventory item: {item_id}")
    return db_item


def get_inventory_item(db: Session, item_id: str) -> Optional[InventoryItem]:
    """
    Get inventory item by ID.
    
    Args:
        db: Database session
        item_id: Inventory item ID
    
    Returns:
        InventoryItem or None if not found
    """
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()


def get_all_inventory_items(db: Session, skip: int = 0, limit: int = 100) -> List[InventoryItem]:
    """
    Get all inventory items with pagination.
    
    Args:
        db: Database session
        skip: Number of items to skip
        limit: Maximum number of items to return
    
    Returns:
        List of InventoryItem
    """
    return db.query(InventoryItem).offset(skip).limit(limit).all()


def update_inventory_item(
    db: Session,
    item_id: str,
    **kwargs
) -> Optional[InventoryItem]:
    """
    Update inventory item fields.
    
    Args:
        db: Database session
        item_id: Inventory item ID
        **kwargs: Fields to update
    
    Returns:
        Updated InventoryItem or None if not found
    """
    item = get_inventory_item(db, item_id)
    
    if not item:
        return None
    
    # Update allowed fields
    allowed_fields = [
        "category", "type", "subtype", "color_name", "color_rgb", "color_group",
        "fit", "formality", "season", "type_confidence", "color_confidence", "image_url"
    ]
    
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    logger.info(f"Updated inventory item: {item_id}")
    return item


def delete_inventory_item(db: Session, item_id: str) -> bool:
    """
    Delete inventory item from database and remove image.
    
    Args:
        db: Database session
        item_id: Inventory item ID
    
    Returns:
        True if deleted, False if not found
    """
    item = get_inventory_item(db, item_id)
    
    if not item:
        return False
    
    # Delete image file
    delete_permanent_image(item_id)
    
    # Delete from database
    db.delete(item)
    db.commit()
    
    logger.info(f"Deleted inventory item: {item_id}")
    return True


def save_from_temporary(
    db: Session,
    temp_id: str,
    inventory_data: dict,
    image_bytes: bytes
) -> InventoryItem:
    """
    Save inventory item from temporary storage to permanent database.
    
    Args:
        db: Database session
        temp_id: Temporary ID
        inventory_data: Inventory item dictionary
        image_bytes: Image bytes to save
    
    Returns:
        Created InventoryItem
    """
    item_id = inventory_data.get("id")
    
    # Move image from temp to permanent
    image_path = move_temp_to_permanent(temp_id, item_id)
    
    if not image_path:
        # If temp image doesn't exist, save directly
        from app.services.image_service import save_permanent_image
        image_path = save_permanent_image(image_bytes, item_id)
    
    # Extract color data
    color = inventory_data.get("color", {})
    
    # Create inventory item
    return create_inventory_item(
        db=db,
        item_id=item_id,
        image_path=image_path,
        category=inventory_data.get("category"),
        item_type=inventory_data.get("type"),
        color_name=color.get("name"),
        color_rgb=color.get("rgb", []),
        color_group=color.get("group"),
        subtype=inventory_data.get("subtype", "unknown"),
        fit=inventory_data.get("fit", "unknown"),
        formality=inventory_data.get("formality", "unknown"),
        season=inventory_data.get("season", [])
    )

