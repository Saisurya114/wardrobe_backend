"""
Permanent inventory API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.models import get_db, InventoryItem
from app.services.inventory_service import (
    create_inventory_item,
    get_inventory_item,
    get_all_inventory_items,
    update_inventory_item,
    delete_inventory_item,
    save_from_temporary
)
from app.services.temporary_inventory import get_temporary_item
from app.services.image_service import get_image_url
import base64

logger = logging.getLogger(__name__)
router = APIRouter()


class InventorySaveRequest(BaseModel):
    """Request model for saving from temporary inventory."""
    temp_id: str


class InventoryUpdateRequest(BaseModel):
    """Request model for updating inventory item."""
    category: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    color_name: Optional[str] = None
    color_rgb: Optional[List[int]] = None
    color_group: Optional[str] = None
    fit: Optional[str] = None
    formality: Optional[str] = None
    season: Optional[List[str]] = None


@router.post("/save")
async def save_inventory_item(
    request: InventorySaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save temporary inventory item to permanent database.
    
    Moves item from temporary_inventory.json to SQLite database
    and saves image to permanent storage.
    """
    # Get temporary item
    temp_item = get_temporary_item(request.temp_id)
    
    if not temp_item:
        raise HTTPException(status_code=404, detail="Temporary item not found")
    
    inventory_data = temp_item.get("inventory", {})
    image_data = temp_item.get("image", {})
    
    # Decode base64 image
    try:
        image_base64 = image_data.get("data", "")
        image_bytes = base64.b64decode(image_base64)
    except Exception as e:
        logger.error(f"Failed to decode image: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid image data")
    
    # Save to permanent database
    try:
        db_item = save_from_temporary(
            db=db,
            temp_id=request.temp_id,
            inventory_data=inventory_data,
            image_bytes=image_bytes
        )
        
        # Generate image URL
        base_url = ""  # Can be set from environment variable
        image_url = get_image_url(db_item.image_path, base_url)
        
        # Update image_url in database
        db_item.image_url = image_url
        db.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "Item saved to inventory",
            "item": db_item.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Error saving inventory item: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save inventory item")


@router.get("")
async def list_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all inventory items with pagination.
    
    Returns list of all confirmed inventory items.
    """
    items = get_all_inventory_items(db, skip=skip, limit=limit)
    
    base_url = ""  # Can be set from environment variable
    
    return JSONResponse(content={
        "success": True,
        "count": len(items),
        "items": [
            {
                **item.to_dict(),
                "image_url": get_image_url(item.image_path, base_url) if not item.image_url else item.image_url
            }
            for item in items
        ]
    })


@router.get("/{item_id}")
async def get_inventory_item_endpoint(
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    Get inventory item by ID.
    
    Returns single inventory item with image URL.
    """
    item = get_inventory_item(db, item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    base_url = ""  # Can be set from environment variable
    image_url = get_image_url(item.image_path, base_url) if not item.image_url else item.image_url
    
    return JSONResponse(content={
        "success": True,
        "item": {
            **item.to_dict(),
            "image_url": image_url
        }
    })


@router.put("/{item_id}")
async def update_inventory_item_endpoint(
    item_id: str,
    request: InventoryUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update inventory item.
    
    Allows updating any inventory fields.
    Only provided fields will be updated.
    """
    update_data = request.dict(exclude_none=True)
    
    # Handle color fields
    if "color_name" in update_data or "color_rgb" in update_data or "color_group" in update_data:
        # If any color field is provided, ensure all are provided or get existing
        item = get_inventory_item(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        # Merge with existing color data
        if "color_name" not in update_data:
            update_data["color_name"] = item.color_name
        if "color_rgb" not in update_data:
            update_data["color_rgb"] = item.color_rgb
        if "color_group" not in update_data:
            update_data["color_group"] = item.color_group
    
    item = update_inventory_item(db, item_id, **update_data)
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    base_url = ""  # Can be set from environment variable
    image_url = get_image_url(item.image_path, base_url) if not item.image_url else item.image_url
    
    return JSONResponse(content={
        "success": True,
        "item": {
            **item.to_dict(),
            "image_url": image_url
        }
    })


@router.delete("/{item_id}")
async def delete_inventory_item_endpoint(
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete inventory item.
    
    Removes item from database and deletes associated image file.
    """
    success = delete_inventory_item(db, item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return JSONResponse(content={
        "success": True,
        "message": "Inventory item deleted"
    })

